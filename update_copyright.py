#!/usr/bin/python
#
# Copyright (C) 2010 W. Trevor King <wking@drexel.edu>
#
# This file is part of Hooke.
#
# Hooke is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Hooke is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Hooke.  If not, see
# <http://www.gnu.org/licenses/>.

"""Automatically update copyright boilerplate.

This script is adapted from one written for `Bugs Everywhere`_.

.. _Bugs Everywhere: http://bugseverywhere.org/
"""

import difflib
import email.utils
import os
import os.path
import re
import StringIO
import sys
import time

import mercurial
import mercurial.dispatch


PROJECT_INFO = {
    'project': 'Hooke',
    'vcs': 'Mercurial',
    }

# Break "copyright" into "copy" and "right" to avoid matching the
# REGEXP.
COPY_RIGHT_TEXT="""
This file is part of %(project)s.

%(project)s is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

%(project)s is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with %(project)s.  If not, see
<http://www.gnu.org/licenses/>.
""".strip()

COPY_RIGHT_TAG='-xyz-COPY' + '-RIGHT-zyx-' # unlikely to occur in the wild :p

ALIASES = {
    'A. Seeholzer':
        ['A. Seeholzer'],
    'Alberto Gomez-Casado':
        ['albertogomcas'],
    'Massimo Sandal <devicerandom@gmail.com>':
        ['Massimo Sandal',
         'devicerandom',
         'unknown'],
    'Fabrizio Benedetti':
        ['fabrizio.benedetti.82'],
    'Richard Naud <richard.naud@epfl.ch>':
        ['Richard Naud'],
    'Rolf Schmidt <rschmidt@alcor.concordia.ca>':
        ['Rolf Schmidt',
         'illysam'],
    'Marco Brucale':
        ['marcobrucale'],
    'Pancaldi Paolo':
        ['pancaldi.paolo'],
    }

IGNORED_PATHS = ['./.hg/', './doc/img', './test/data/',
                 './build/', '/doc/build/']
IGNORED_FILES = ['COPYING', 'COPYING.LESSER']

# Work around missing author holes in the VCS history
AUTHOR_HACKS = {
    ('hooke','driver','hdf5.py'):['Massimo Sandal'],
    ('hooke','driver','mcs.py'):['Allen Chen'],
    ('hooke','driver','mfp3d.py'):['A. Seeholzer','Richard Naud','Rolf Schmidt',
                                   'Alberto Gomez-Casado'],
    ('hooke','plugin','peakspot.py'):['Fabrizio Benedetti'],
    ('hooke','plugin','showconvoluted.py'):['Rolf Schmidt'],
    ('hooke','ui','gui','formatter.py'):['Francesco Musiani','Massimo Sandal'],
    ('hooke','ui','gui','prettyformat.py'):['Rolf Schmidt'],
    }

# Work around missing year holes in the VCS history
YEAR_HACKS = {
    ('hooke','driver','hdf5.py'):2009,
    ('hooke','driver','mfp3d.py'):2008,
    ('hooke','driver','picoforce.py'):2006,
    ('hooke','driver','picoforcealt.py'):2006,
    ('hooke','plugin','peakspot.py'):2007,
    ('hooke','plugin','showconvoluted.py'):2009,
    ('hooke','plugin','tutorial.py'):2007,
    ('hooke','ui','gui','formatter.py'):2006,
    ('hooke','ui','gui','prettyformat.py'):2009,
    }

# Helpers for VCS-specific commands

def splitpath(path):
    """Recursively split a path into elements.

    Examples
    --------

    >>> splitpath(os.path.join('a', 'b', 'c'))
    ('a', 'b', 'c')
    >>> splitpath(os.path.join('.', 'a', 'b', 'c'))
    ('a', 'b', 'c')
    """
    path = os.path.normpath(path)
    elements = []
    while True:
        dirname,basename = os.path.split(path)
        elements.insert(0,basename)
        if dirname in ['', '.']:
            break
        path = dirname
    return tuple(elements)

# VCS-specific commands

def mercurial_cmd(*args):
    cwd = os.getcwd()
    stdout = sys.stdout
    stderr = sys.stderr
    tmp_stdout = StringIO.StringIO()
    tmp_stderr = StringIO.StringIO()
    sys.stdout = tmp_stdout
    sys.stderr = tmp_stderr
    try:
        mercurial.dispatch.dispatch(list(args))
    finally:
        os.chdir(cwd)
        sys.stdout = stdout
        sys.stderr = stderr
    return (tmp_stdout.getvalue().rstrip('\n'),
            tmp_stderr.getvalue().rstrip('\n'))

def original_year(filename, year_hacks=YEAR_HACKS):
    # shortdate filter: YEAR-MONTH-DAY
    output,error = mercurial_cmd('log', '--follow',
                                 '--template', '{date|shortdate}\n',
                                 filename)
    years = [int(line.split('-', 1)[0]) for line in output.splitlines()]
    if splitpath(filename) in year_hacks:
        years.append(year_hacks[splitpath(filename)])
    years.sort()
    return years[0]

def authors(filename, author_hacks=AUTHOR_HACKS):
    output,error = mercurial_cmd('log', '--follow',
                                 '--template', '{author}\n',
                                 filename)
    ret = list(set(output.splitlines()))
    if splitpath(filename) in author_hacks:
        ret.extend(author_hacks[splitpath(filename)])
    return ret

def authors_list(author_hacks=AUTHOR_HACKS):
    output,error = mercurial_cmd('log', '--follow',
                                 '--template', '{author}\n')
    ret = list(set(output.splitlines()))
    for path,authors in author_hacks.items():
        ret.extend(authors)
    return ret

def is_versioned(filename):
    output,error = mercurial_cmd('log', '--follow',
                                 '--template', '{date|shortdate}\n',
                                 filename)
    if len(error) > 0:
        return False
    return True

# General utility commands

def _strip_email(*args):
    """Remove email addresses from a series of names.

    Examples
    --------

    >>> _strip_email('J Doe <jdoe@a.com>')
    ['J Doe']
    >>> _strip_email('J Doe <jdoe@a.com>', 'JJJ Smith <jjjs@a.com>')
    ['J Doe', 'JJJ Smith']
    """
    args = list(args)
    for i,arg in enumerate(args):
        if arg == None:
            continue
        author,addr = email.utils.parseaddr(arg)
        args[i] = author
    return args

def _reverse_aliases(aliases):
    """Reverse an `aliases` dict.

    Input:   key: canonical name,  value: list of aliases
    Output:  key: alias,           value: canonical name

    Examples
    --------

    >>> aliases = {
    ...     'J Doe <jdoe@a.com>':['Johnny <jdoe@b.edu>', 'J'],
    ...     'JJJ Smith <jjjs@a.com>':['Jingly <jjjs@b.edu>'],
    ...     None:['Anonymous <a@a.com>'],
    ...     }
    >>> r = _reverse_aliases(aliases)
    >>> for item in sorted(r.items()):
    ...     print item
    ('Anonymous <a@a.com>', None)
    ('J', 'J Doe <jdoe@a.com>')
    ('Jingly <jjjs@b.edu>', 'JJJ Smith <jjjs@a.com>')
    ('Johnny <jdoe@b.edu>', 'J Doe <jdoe@a.com>')
    """
    output = {}
    for canonical_name,_aliases in aliases.items():
        for alias in _aliases:
            output[alias] = canonical_name
    return output

def _replace_aliases(authors, with_email=True, aliases=None):
    """Consolidate and sort `authors`.

    Make the replacements listed in the `aliases` dict (key: canonical
    name, value: list of aliases).  If `aliases` is ``None``, default
    to ``ALIASES``.

    >>> aliases = {
    ...     'J Doe <jdoe@a.com>':['Johnny <jdoe@b.edu>'],
    ...     'JJJ Smith <jjjs@a.com>':['Jingly <jjjs@b.edu>'],
    ...     None:['Anonymous <a@a.com>'],
    ...     }
    >>> _replace_aliases(['JJJ Smith <jjjs@a.com>', 'Johnny <jdoe@b.edu>',
    ...                   'Jingly <jjjs@b.edu>', 'Anonymous <a@a.com>'],
    ...                  with_email=True, aliases=aliases)
    ['J Doe <jdoe@a.com>', 'JJJ Smith <jjjs@a.com>']
    >>> _replace_aliases(['JJJ Smith', 'Johnny', 'Jingly', 'Anonymous'],
    ...                  with_email=False, aliases=aliases)
    ['J Doe', 'JJJ Smith']
    >>> _replace_aliases(['JJJ Smith <jjjs@a.com>', 'Johnny <jdoe@b.edu>',
    ...                   'Jingly <jjjs@b.edu>', 'J Doe <jdoe@a.com>'],
    ...                  with_email=True, aliases=aliases)
    ['J Doe <jdoe@a.com>', 'JJJ Smith <jjjs@a.com>']
    """
    if aliases == None:
        aliases = ALIASES
    if with_email == False:
        aliases = dict([(_strip_email(author)[0], _strip_email(*_aliases))
                        for author,_aliases in aliases.items()])
    rev_aliases = _reverse_aliases(aliases)
    for i,author in enumerate(authors):
        if author in rev_aliases:
            authors[i] = rev_aliases[author]
    authors = sorted(list(set(authors)))
    if None in authors:
        authors.remove(None)
    return authors

def _copyright_string(original_year, final_year, authors, prefix=''):
    """
    >>> print _copyright_string(original_year=2005,
    ...                         final_year=2005,
    ...                         authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                         prefix='# '
    ...                        ) # doctest: +ELLIPSIS
    # Copyright (C) 2005 A <a@a.com>
    #                    B <b@b.edu>
    #
    # This file...
    >>> print _copyright_string(original_year=2005,
    ...                         final_year=2009,
    ...                         authors=['A <a@a.com>', 'B <b@b.edu>']
    ...                        ) # doctest: +ELLIPSIS
    Copyright (C) 2005-2009 A <a@a.com>
                            B <b@b.edu>
    <BLANKLINE>
    This file...
    """
    if original_year == final_year:
        date_range = '%s' % original_year
    else:
        date_range = '%s-%s' % (original_year, final_year)
    lines = ['Copyright (C) %s %s' % (date_range, authors[0])]
    for author in authors[1:]:
        lines.append(' '*(len('Copyright (C) ')+len(date_range)+1) +
                     author)
    lines.append('')
    lines.extend((COPY_RIGHT_TEXT % PROJECT_INFO).splitlines())
    for i,line in enumerate(lines):
        lines[i] = (prefix + line).rstrip()
    return '\n'.join(lines)

def _tag_copyright(contents):
    """
    >>> contents = '''Some file
    ... bla bla
    ... # Copyright (copyright begins)
    ... # (copyright continues)
    ... # bla bla bla
    ... (copyright ends)
    ... bla bla bla
    ... '''
    >>> print _tag_copyright(contents).replace('COPY-RIGHT', 'CR')
    Some file
    bla bla
    -xyz-CR-zyx-
    (copyright ends)
    bla bla bla
    <BLANKLINE>
    """
    lines = []
    incopy = False
    for line in contents.splitlines():
        if incopy == False and line.startswith('# Copyright'):
            incopy = True
            lines.append(COPY_RIGHT_TAG)
        elif incopy == True and not line.startswith('#'):
            incopy = False
        if incopy == False:
            lines.append(line.rstrip('\n'))
    return '\n'.join(lines)+'\n'

def _update_copyright(contents, original_year, authors):
    """
    >>> contents = '''Some file
    ... bla bla
    ... # Copyright (copyright begins)
    ... # (copyright continues)
    ... # bla bla bla
    ... (copyright ends)
    ... bla bla bla
    ... '''
    >>> print _update_copyright(contents, 2008, ['Jack', 'Jill']
    ...     ) # doctest: +ELLIPSIS, +REPORT_UDIFF
    Some file
    bla bla
    # Copyright (C) 2008-... Jack
    #                         Jill
    #
    # This file...
    (copyright ends)
    bla bla bla
    <BLANKLINE>
    """
    current_year = time.gmtime()[0]
    copyright_string = _copyright_string(
        original_year, current_year, authors, prefix='# ')
    contents = _tag_copyright(contents)
    return contents.replace(COPY_RIGHT_TAG, copyright_string)

def ignored_file(filename, ignored_paths=None, ignored_files=None,
                 check_disk=True, check_vcs=True):
    """
    >>> ignored_paths = ['./a/', './b/']
    >>> ignored_files = ['x', 'y']
    >>> ignored_file('./a/z', ignored_paths, ignored_files, False, False)
    True
    >>> ignored_file('./ab/z', ignored_paths, ignored_files, False, False)
    False
    >>> ignored_file('./ab/x', ignored_paths, ignored_files, False, False)
    True
    >>> ignored_file('./ab/xy', ignored_paths, ignored_files, False, False)
    False
    >>> ignored_file('./z', ignored_paths, ignored_files, False, False)
    False
    """
    if ignored_paths == None:
        ignored_paths = IGNORED_PATHS
    if ignored_files == None:
        ignored_files = IGNORED_FILES
    if check_disk == True and os.path.isfile(filename) == False:
        return True
    for path in ignored_paths:
        if filename.startswith(path):
            return True
    if os.path.basename(filename) in ignored_files:
        return True
    if check_vcs == True and is_versioned(filename) == False:
        return True
    return False

def _set_contents(filename, contents, original_contents=None, dry_run=False,
                  verbose=0):
    if original_contents == None and os.path.isfile(filename):
        f = open(filename, 'r')
        original_contents = f.read()
        f.close()
    if verbose > 0:
        print "checking %s ... " % filename,
    if contents != original_contents:
        if verbose > 0:
            if original_contents == None:
                print "[creating]"
            else:
                print "[updating]"
        if verbose > 1 and original_contents != None:
            print '\n'.join(
                difflib.unified_diff(
                    original_contents.splitlines(), contents.splitlines(),
                    fromfile=os.path.normpath(os.path.join('a', filename)),
                    tofile=os.path.normpath(os.path.join('b', filename)),
                    n=3, lineterm=''))
        if dry_run == False:
            f = file(filename, 'w')
            f.write(contents)
            f.close()
    elif verbose > 0:
        print "[no change]"

# Update commands

def update_authors(authors_fn=authors_list, dry_run=False, verbose=0):
    authors = authors_fn()
    authors = _replace_aliases(authors, with_email=True, aliases=ALIASES)
    new_contents = '%s was written by:\n%s\n' % (
        PROJECT_INFO['project'],
        '\n'.join(authors)
        )
    _set_contents('AUTHORS', new_contents, dry_run=dry_run, verbose=verbose)

def update_file(filename, original_year_fn=original_year, authors_fn=authors,
                dry_run=False, verbose=0):
    f = file(filename, 'r')
    contents = f.read()
    f.close()

    original_year = original_year_fn(filename)
    authors = authors_fn(filename)
    authors = _replace_aliases(authors, with_email=True, aliases=ALIASES)

    new_contents = _update_copyright(contents, original_year, authors)
    _set_contents(filename, contents=new_contents, original_contents=contents,
                  dry_run=dry_run, verbose=verbose)

def update_files(files=None, dry_run=False, verbose=0):
    if files == None or len(files) == 0:
        files = []
        for dirpath,dirnames,filenames in os.walk('.'):
            for filename in filenames:
                files.append(os.path.join(dirpath, filename))

    for filename in files:
        if ignored_file(filename) == True:
            continue
        update_file(filename, dry_run=dry_run, verbose=verbose)

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    import optparse
    import sys

    usage = """%%prog [options] [file ...]

Update copyright information in source code with information from
the %(vcs)s repository.  Run from the %(project)s repository root.

Replaces every line starting with '^# Copyright' and continuing with
'^#' with an auto-generated copyright blurb.  If you want to add
#-commented material after a copyright blurb, please insert a blank
line between the blurb and your comment, so the next run of
``update_copyright.py`` doesn't clobber your comment.

If no files are given, a list of files to update is generated
automatically.
""" % PROJECT_INFO
    p = optparse.OptionParser(usage)
    p.add_option('--test', dest='test', default=False,
                 action='store_true', help='Run internal tests and exit')
    p.add_option('--dry-run', dest='dry_run', default=False,
                 action='store_true', help="Don't make any changes")
    p.add_option('-v', '--verbose', dest='verbose', default=0,
                 action='count', help='Increment verbosity')
    options,args = p.parse_args()

    if options.test == True:
        test()
        sys.exit(0)

    update_authors(dry_run=options.dry_run, verbose=options.verbose)
    update_files(files=args, dry_run=options.dry_run, verbose=options.verbose)
