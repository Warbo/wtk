# Copyright

import difflib as _difflib
import os as _os
import os.path as _os_path
import textwrap as _textwrap
import time as _time

from . import LOG as _LOG


def long_author_formatter(copyright_year_string, authors):
    """
    >>> print '\\n'.join(long_author_formatter(
    ...     copyright_year_string='Copyright (C) 1990-2010',
    ...     authors=['Jack', 'Jill', 'John']))
    Copyright (C) 1990-2010 Jack
                            Jill
                            John
    """
    lines = ['%s %s' % (copyright_year_string, authors[0])]
    for author in authors[1:]:
        lines.append(' '*(len(copyright_year_string)+1) + author)
    return lines

def short_author_formatter(copyright_year_string, authors):
    """
    >>> print '\\n'.join(short_author_formatter(
    ...     copyright_year_string='Copyright (C) 1990-2010',
    ...     authors=['Jack', 'Jill', 'John']*5))
    Copyright (C) 1990-2010 Jack, Jill, John, Jack, Jill, John, Jack, Jill, John, Jack, Jill, John, Jack, Jill, John
    """
    blurb = '%s %s' % (copyright_year_string, ', '.join(authors))
    return [blurb]

def copyright_string(original_year, final_year, authors, text, info={},
                     author_format_fn=long_author_formatter,
                     formatter_kwargs={}, prefix='', wrap=True,
                     **wrap_kwargs):
    """
    >>> print(copyright_string(original_year=2005, final_year=2005,
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=['BLURB',], prefix='# '
    ...                        )) # doctest: +REPORT_UDIFF
    # Copyright (C) 2005 A <a@a.com>
    #                    B <b@b.edu>
    #
    # BLURB
    >>> print(copyright_string(original_year=2005, final_year=2009,
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=['BLURB',]
    ...                        )) # doctest: +REPORT_UDIFF
    Copyright (C) 2005-2009 A <a@a.com>
                            B <b@b.edu>
    <BLANKLINE>
    BLURB
    >>> print(copyright_string(original_year=2005, final_year=2005,
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=['This file is part of %(program)s.',],
    ...                        author_format_fn=short_author_formatter,
    ...                        info={'program':'update-copyright'},
    ...                        width=25,
    ...                        )) # doctest: +REPORT_UDIFF
    Copyright (C) 2005 A <a@a.com>, B <b@b.edu>
    <BLANKLINE>
    This file is part of
    update-copyright.
    >>> print(copyright_string(original_year=2005, final_year=2005,
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=[('This file is part of %(program)s.  '*3
    ...                               ).strip(),],
    ...                        info={'program':'update-copyright'},
    ...                        author_format_fn=short_author_formatter,
    ...                        wrap=False,
    ...                        )) # doctest: +REPORT_UDIFF
    Copyright (C) 2005 A <a@a.com>, B <b@b.edu>
    <BLANKLINE>
    This file is part of update-copyright.  This file is part of update-copyright.  This file is part of update-copyright.
    """
    for key in ['initial_indent', 'subsequent_indent']:
        if key not in wrap_kwargs:
            wrap_kwargs[key] = prefix

    if original_year == final_year:
        date_range = '%s' % original_year
    else:
        date_range = '%s-%s' % (original_year, final_year)
    copyright_year_string = 'Copyright (C) %s' % date_range

    lines = author_format_fn(copyright_year_string, authors,
                             **formatter_kwargs)
    for i,line in enumerate(lines):
        lines[i] = prefix + line

    for i,paragraph in enumerate(text):
        try:
            text[i] = paragraph % info
        except ValueError, e:
            _LOG.error(
                "{}: can't format {} with {}".format(e, paragraph, info))
            raise
        except TypeError, e:
            _LOG.error(
                ('{}: copright text must be a list of paragraph strings, '
                 'not {}').format(e, repr(text)))
            raise

    if wrap == True:
        text = [_textwrap.fill(p, **wrap_kwargs) for p in text]
    else:
        assert wrap_kwargs['subsequent_indent'] == '', \
            wrap_kwargs['subsequent_indent']
    sep = '\n%s\n' % prefix.rstrip()
    return sep.join(['\n'.join(lines)] + text)

def tag_copyright(contents, tag=None):
    """
    >>> contents = '''Some file
    ... bla bla
    ... # Copyright (copyright begins)
    ... # (copyright continues)
    ... # bla bla bla
    ... (copyright ends)
    ... bla bla bla
    ... '''
    >>> print tag_copyright(contents, tag='-xyz-CR-zyx-')
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
            lines.append(tag)
        elif incopy == True and not line.startswith('#'):
            incopy = False
        if incopy == False:
            lines.append(line.rstrip('\n'))
    return '\n'.join(lines)+'\n'

def update_copyright(contents, tag=None, **kwargs):
    """
    >>> contents = '''Some file
    ... bla bla
    ... # Copyright (copyright begins)
    ... # (copyright continues)
    ... # bla bla bla
    ... (copyright ends)
    ... bla bla bla
    ... '''
    >>> print update_copyright(contents, original_year=2008,
    ...                        authors=['Jack', 'Jill'],
    ...                        text=['BLURB',], prefix='# ', tag='--tag--'
    ...     ) # doctest: +ELLIPSIS, +REPORT_UDIFF
    Some file
    bla bla
    # Copyright (C) 2008-... Jack
    #                         Jill
    #
    # BLURB
    (copyright ends)
    bla bla bla
    <BLANKLINE>
    """
    current_year = _time.gmtime()[0]
    string = copyright_string(final_year=current_year, **kwargs)
    contents = tag_copyright(contents=contents, tag=tag)
    return contents.replace(tag, string)

def get_contents(filename):
    if _os_path.isfile(filename):
        f = open(filename, 'r')
        contents = f.read()
        f.close()
        return contents
    return None

def set_contents(filename, contents, original_contents=None, dry_run=False):
    if original_contents is None:
        original_contents = get_contents(filename=filename)
    _LOG.debug('check contents of {}'.format(filename))
    if contents != original_contents:
        if original_contents is None:
            _LOG.info('creating {}'.format(filename))
        else:
            _LOG.info('updating {}'.format(filename))
            _LOG.debug('\n'.join(
                    _difflib.unified_diff(
                        original_contents.splitlines(), contents.splitlines(),
                        fromfile=_os_path.normpath(
                            _os_path.join('a', filename)),
                        tofile=_os_path.normpath(_os_path.join('b', filename)),
                        n=3, lineterm='')))
        if dry_run == False:
            f = file(filename, 'w')
            f.write(contents)
            f.close()
    _LOG.debug('no change in {}'.format(filename))

def list_files(root='.'):
    for dirpath,dirnames,filenames in _os.walk(root):
        for filename in filenames:
            yield _os_path.join(root, dirpath, filename)
