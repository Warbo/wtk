# Copyright (C) 2012-2014 W. Trevor King <wking@tremily.us>
#
# This file is part of update-copyright.
#
# update-copyright is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# update-copyright is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# update-copyright.  If not, see <http://www.gnu.org/licenses/>.

import codecs as _codecs
import difflib as _difflib
import locale as _locale
import os as _os
import os.path as _os_path
import sys as _sys
import textwrap as _textwrap

from . import LOG as _LOG


ENCODING = _locale.getpreferredencoding() or _sys.getdefaultencoding()


def long_author_formatter(copyright_year_string, authors):
    """
    >>> print('\\n'.join(long_author_formatter(
    ...     copyright_year_string='Copyright (C) 1990-2010',
    ...     authors=['Jack', 'Jill', 'John'])))
    Copyright (C) 1990-2010 Jack
                            Jill
                            John
    """
    lines = ['{} {}'.format(copyright_year_string, authors[0])]
    for author in authors[1:]:
        lines.append(' '*(len(copyright_year_string)+1) + author)
    return lines

def short_author_formatter(copyright_year_string, authors):
    """
    >>> print('\\n'.join(short_author_formatter(
    ...     copyright_year_string='Copyright (C) 1990-2010',
    ...     authors=['Jack', 'Jill', 'John']*5)))
    Copyright (C) 1990-2010 Jack, Jill, John, Jack, Jill, John, Jack, Jill, John, Jack, Jill, John, Jack, Jill, John
    """
    blurb = '{} {}'.format(copyright_year_string, ', '.join(authors))
    return [blurb]

def copyright_string(years, authors, text, info={},
                     author_format_fn=long_author_formatter,
                     formatter_kwargs={}, prefix=('', '', None), wrap=True,
                     **wrap_kwargs):
    """
    >>> print(copyright_string(years=[2005],
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=['BLURB',], prefix=('# ', '# ', None),
    ...                        )) # doctest: +REPORT_UDIFF
    # Copyright (C) 2005 A <a@a.com>
    #                    B <b@b.edu>
    #
    # BLURB
    >>> print(copyright_string(years=[2005, 2009],
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=['BLURB',], prefix=('/* ', ' * ', ' */'),
    ...                        )) # doctest: +REPORT_UDIFF
    /* Copyright (C) 2005-2009 A <a@a.com>
     *                         B <b@b.edu>
     *
     * BLURB
     */
    >>> print(copyright_string(years=[2005, 2009],
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=['BLURB',]
    ...                        )) # doctest: +REPORT_UDIFF
    Copyright (C) 2005-2009 A <a@a.com>
                            B <b@b.edu>
    <BLANKLINE>
    BLURB
    >>> print(copyright_string(years=[2005],
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=['This file is part of {program}.',],
    ...                        author_format_fn=short_author_formatter,
    ...                        info={'program':'update-copyright'},
    ...                        width=25,
    ...                        )) # doctest: +REPORT_UDIFF
    Copyright (C) 2005 A <a@a.com>, B <b@b.edu>
    <BLANKLINE>
    This file is part of
    update-copyright.
    >>> print(copyright_string(years=[2005],
    ...                        authors=['A <a@a.com>', 'B <b@b.edu>'],
    ...                        text=[('This file is part of {program}.  '*3
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
            wrap_kwargs[key] = prefix[1]

    if not years:
        raise ValueError('empty years argument: {!r}'.format(years))
    elif len(years) == 1:
        date_range = str(years[0])
    else:
        original_year = min(years)
        final_year = max(years)
        date_range = '{}-{}'.format(original_year, final_year)
    copyright_year_string = 'Copyright (C) {}'.format(date_range)

    lines = author_format_fn(copyright_year_string, authors,
                             **formatter_kwargs)
    for i,line in enumerate(lines):
        if i == 0:
            lines[i] = prefix[0] + line
        else:
            lines[i] = prefix[1] + line

    for i,paragraph in enumerate(text):
        try:
            text[i] = paragraph.format(**info)
        except ValueError as e:
            _LOG.error(
                "{}: can't format {} with {}".format(e, paragraph, info))
            raise
        except TypeError as e:
            _LOG.error(
                ('{}: copright text must be a list of paragraph strings, '
                 'not {}').format(e, repr(text)))
            raise

    if wrap == True:
        text = [_textwrap.fill(p, **wrap_kwargs) for p in text]
    else:
        assert wrap_kwargs['subsequent_indent'] == '', \
            wrap_kwargs['subsequent_indent']
    sep = '\n{}\n'.format(prefix[1].rstrip())
    ret = sep.join(['\n'.join(lines)] + text)
    if prefix[2]:
        ret += ('\n{}'.format(prefix[2]))
    return ret

def tag_copyright(contents, prefix=('# ', '# ', None), tag=None):
    """
    >>> contents = '''Some file
    ... bla bla
    ... # Copyright (copyright begins)
    ... # (copyright continues)
    ... # bla bla bla
    ... (copyright ends)
    ... bla bla bla
    ... '''
    >>> print(tag_copyright(contents, tag='-xyz-CR-zyx-'))
    Some file
    bla bla
    -xyz-CR-zyx-
    (copyright ends)
    bla bla bla
    <BLANKLINE>
    >>> contents = '''Some file
    ... bla bla
    ... /* Copyright (copyright begins)
    ...  * (copyright continues)
    ...  *
    ...  * bla bla bla
    ...  */
    ... (copyright ends)
    ... bla bla bla
    ... '''
    >>> print(tag_copyright(
    ...     contents, prefix=('/* ', ' * ', ' */'), tag='-xyz-CR-zyx-'))
    Some file
    bla bla
    -xyz-CR-zyx-
    (copyright ends)
    bla bla bla
    <BLANKLINE>
    """
    lines = []
    incopy = False
    start = prefix[0] + 'Copyright'
    middle = prefix[1].rstrip()
    end = prefix[2]
    for line in contents.splitlines():
        if not incopy and line.startswith(start):
            incopy = True
            lines.append(tag)
        elif incopy and not line.startswith(middle):
            if end:
                assert line.startswith(end), line
            incopy = False
        if not incopy:
            lines.append(line.rstrip('\n'))
        if incopy and end and line.startswith(end):
            incopy = False
    return '\n'.join(lines)+'\n'

def update_copyright(contents, prefix=('# ', '# ', None), tag=None, **kwargs):
    """
    >>> contents = '''Some file
    ... bla bla
    ... # Copyright (copyright begins)
    ... # (copyright continues)
    ... # bla bla bla
    ... (copyright ends)
    ... bla bla bla
    ... '''
    >>> print(update_copyright(
    ...     contents, years=[2008], authors=['Jack', 'Jill'],
    ...     text=['BLURB',], prefix=('# ', '# ', None), tag='--tag--'
    ...     )) # doctest: +ELLIPSIS, +REPORT_UDIFF
    Some file
    bla bla
    # Copyright (C) 2008 Jack
    #                    Jill
    #
    # BLURB
    (copyright ends)
    bla bla bla
    <BLANKLINE>
    """
    string = copyright_string(prefix=prefix, **kwargs)
    contents = tag_copyright(contents=contents, prefix=prefix, tag=tag)
    return contents.replace(tag, string)

def get_contents(filename, unicode=False, encoding=None):
    if _os_path.isfile(filename):
        if unicode:
            if encoding is None:
                encoding = ENCODING
            f = _codecs.open(filename, 'r', encoding=encoding)
        else:
            f = open(filename, 'r')
        contents = f.read()
        f.close()
        return contents
    return None

def set_contents(filename, contents, original_contents=None, unicode=False,
                 encoding=None, dry_run=False):
    if original_contents is None:
        original_contents = get_contents(
            filename=filename, unicode=unicode, encoding=encoding)
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
            if unicode:
                if encoding is None:
                    encoding = ENCODING
                f = _codecs.open(filename, 'w', encoding=encoding)
            else:
                f = file(filename, 'w')
            f.write(contents)
            f.close()
    _LOG.debug('no change in {}'.format(filename))

def list_files(root='.'):
    for dirpath,dirnames,filenames in _os.walk(root):
        for filename in filenames:
            yield _os_path.normpath(_os_path.join(root, dirpath, filename))
