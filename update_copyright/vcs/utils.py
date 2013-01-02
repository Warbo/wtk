# Copyright (C) 2012-2013 W. Trevor King <wking@tremily.us>
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

"""Useful utilities for backend classes."""

import email.utils as _email_utils
import os.path as _os_path
import subprocess as _subprocess
import sys as _sys

from .. import LOG as LOG
from ..utils import ENCODING as _ENCODING


_MSWINDOWS = _sys.platform == 'win32'
_POSIX = not _MSWINDOWS


def invoke(args, stdin=None, stdout=_subprocess.PIPE, stderr=_subprocess.PIPE,
           cwd=None, expect=(0,), unicode_output=False, encoding=None):
    """Invoke an external program and return the results

    ``expect`` should be a tuple of allowed exit codes.

    When ``unicode_output`` is ``True``, convert stdout and stdin
    strings to unicode before returing them.
    """
    LOG.debug('{}$ {}'.format(cwd, args))
    try :
        if _POSIX:
            q = _subprocess.Popen(args, stdin=_subprocess.PIPE,
                                  stdout=stdout, stderr=stderr,
                                  close_fds=True, cwd=cwd)
        else:
            assert _MSWINDOWS == True, 'invalid platform'
            # win32 don't have os.execvp() so run the command in a shell
            q = _subprocess.Popen(args, stdin=_subprocess.PIPE,
                                  stdout=stdout, stderr=stderr, shell=True,
                                  cwd=cwd)
    except OSError as e:
        raise ValueError([args, e])
    stdout,stderr = q.communicate(input=stdin)
    status = q.wait()
    if unicode_output == True:
        if encoding is None:
            encoding = _ENCODING
        if stdout is not None:
            stdout = str(stdout, encoding)
        if stderr is not None:
            stderr = str(stderr, encoding)
    if status not in expect:
        raise ValueError([args, status, stdout, stderr])
    return status, stdout, stderr

def splitpath(path):
    """Recursively split a path into elements.

    Examples
    --------

    >>> import os.path
    >>> splitpath(os.path.join('a', 'b', 'c'))
    ('a', 'b', 'c')
    >>> splitpath(os.path.join('.', 'a', 'b', 'c'))
    ('a', 'b', 'c')
    """
    path = _os_path.normpath(path)
    elements = []
    while True:
        dirname,basename = _os_path.split(path)
        elements.insert(0,basename)
        if dirname in ['/', '', '.']:
            break
        path = dirname
    return tuple(elements)

def strip_email(*args):
    """Remove email addresses from a series of names.

    Examples
    --------

    >>> strip_email('J Doe')
    ['J Doe']
    >>> strip_email('J Doe <jdoe@a.com>')
    ['J Doe']
    >>> strip_email('J Doe <jdoe@a.com>', 'JJJ Smith <jjjs@a.com>')
    ['J Doe', 'JJJ Smith']
    """
    args = list(args)
    for i,arg in enumerate(args):
        if arg == None:
            continue
        author,addr = _email_utils.parseaddr(arg)
        if author == '':
            author = arg
        args[i] = author
    return args

def reverse_aliases(aliases):
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
    >>> r = reverse_aliases(aliases)
    >>> for item in sorted(r.items()):
    ...     print(item)
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

def replace_aliases(authors, with_email=True, aliases=None):
    """Consolidate and sort `authors`.

    Make the replacements listed in the `aliases` dict (key: canonical
    name, value: list of aliases).  If `aliases` is ``None``, default
    to ``ALIASES``.

    >>> aliases = {
    ...     'J Doe <jdoe@a.com>':['Johnny <jdoe@b.edu>'],
    ...     'JJJ Smith <jjjs@a.com>':['Jingly <jjjs@b.edu>'],
    ...     None:['Anonymous <a@a.com>'],
    ...     }
    >>> authors = [
    ...     'JJJ Smith <jjjs@a.com>', 'Johnny <jdoe@b.edu>',
    ...     'Jingly <jjjs@b.edu>', 'J Doe <jdoe@a.com>', 'Anonymous <a@a.com>']
    >>> replace_aliases(authors, with_email=True, aliases=aliases)
    ['J Doe <jdoe@a.com>', 'JJJ Smith <jjjs@a.com>']
    >>> replace_aliases(authors, with_email=False, aliases=aliases)
    ['J Doe', 'JJJ Smith']
    """
    if aliases == None:
        aliases = ALIASES
    rev_aliases = reverse_aliases(aliases)
    authors = list(authors)
    for i,author in enumerate(authors):
        if author in rev_aliases:
            authors[i] = rev_aliases[author]
    authors = set(authors)
    try:
        authors.remove(None)
    except KeyError:
        pass
    authors = sorted(authors)
    if with_email == False:
        authors = strip_email(*authors)
    return authors
