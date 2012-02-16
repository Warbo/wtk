# Copyright

"""Useful utilities for backend classes."""

import email.utils as _email_utils
import os.path as _os_path
import subprocess as _subprocess
import sys as _sys


_MSWINDOWS = _sys.platform == 'win32'
_POSIX = not _MSWINDOWS


def invoke(args, stdin=None, stdout=_subprocess.PIPE, stderr=_subprocess.PIPE,
           expect=(0,)):
    """
    expect should be a tuple of allowed exit codes.
    """
    try :
        if _POSIX:
            q = _subprocess.Popen(args, stdin=_subprocess.PIPE,
                                  stdout=stdout, stderr=stderr)
        else:
            assert _MSWINDOWS == True, 'invalid platform'
            # win32 don't have os.execvp() so run the command in a shell
            q = _subprocess.Popen(args, stdin=_subprocess.PIPE,
                                  stdout=stdout, stderr=stderr, shell=True)
    except OSError, e:
        raise ValueError([args, e])
    stdout,stderr = q.communicate(input=stdin)
    status = q.wait()
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
        if dirname in ['', '.']:
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
    for i,author in enumerate(authors):
        if author in rev_aliases:
            authors[i] = rev_aliases[author]
    authors = sorted(list(set(authors)))
    if None in authors:
        authors.remove(None)
    if with_email == False:
        authors = strip_email(*authors)
    return authors
