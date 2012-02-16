# Copyright (C) 2012 W. Trevor King
#
# This file is part of update-copyright.
#
# update-copyright is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# update-copyright is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with update-copyright.  If not, see
# <http://www.gnu.org/licenses/>.

"""Project-specific configuration.

# Convert author names to canonical forms.
# ALIASES[<canonical name>] = <list of aliases>
# for example,
# ALIASES = {
#     'John Doe <jdoe@a.com>':
#         ['John Doe', 'jdoe', 'J. Doe <j@doe.net>'],
#     }
# Git-based projects are encouraged to use .mailmap instead of
# ALIASES.  See git-shortlog(1) for details.

# List of paths that should not be scanned for copyright updates.
# IGNORED_PATHS = ['./.git/']
IGNORED_PATHS = ['./.git']
# List of files that should not be scanned for copyright updates.
# IGNORED_FILES = ['COPYING']
IGNORED_FILES = ['COPYING']

# Work around missing author holes in the VCS history.
# AUTHOR_HACKS[<path tuple>] = [<missing authors]
# for example, if John Doe contributed to module.py but wasn't listed
# in the VCS history of that file:
# AUTHOR_HACKS = {
#     ('path', 'to', 'module.py'):['John Doe'],
#     }
AUTHOR_HACKS = {}

# Work around missing year holes in the VCS history.
# YEAR_HACKS[<path tuple>] = <original year>
# for example, if module.py was published in 2008 but the VCS history
# only goes back to 2010:
# YEAR_HACKS = {
#     ('path', 'to', 'module.py'):2008,
#     }
YEAR_HACKS = {}
"""

import ConfigParser as _configparser
import fnmatch as _fnmatch
import os.path as _os_path
import sys
import time as _time

from . import LOG as _LOG
from . import utils as _utils
from .vcs.git import GitBackend as _GitBackend
try:
    from .vcs.bazaar import BazaarBackend as _BazaarBackend
except ImportError, _bazaar_import_error:
    _BazaarBackend = None
try:
    from .vcs.mercurial import MercurialBackend as _MercurialBackend
except ImportError, _mercurial_import_error:
    _MercurialBackend = None


class Project (object):
    def __init__(self, name=None, vcs=None, copyright=None,
                 short_copyright=None):
        self._name = name
        self._vcs = vcs
        self._copyright = None
        self._short_copyright = None
        self.with_authors = False
        self.with_files = False
        self._ignored_paths = None
        self._pyfile = None

        # unlikely to occur in the wild :p
        self._copyright_tag = '-xyz-COPY' + '-RIGHT-zyx-'

    def load_config(self, stream):
        p = _configparser.RawConfigParser()
        p.readfp(stream)
        try:
            self._name = p.get('project', 'name')
        except _configparser.NoOptionError:
            pass
        try:
            vcs = p.get('project', 'vcs')
        except _configparser.NoOptionError:
            pass
        else:
            if vcs == 'Git':
                self._vcs = _GitBackend()
            elif vcs == 'Bazaar':
                self._vcs = _BazaarBackend()
            elif vcs == 'Mercurial':
                self._vcs = _MercurialBackend()
            else:
                raise NotImplementedError('vcs: {}'.format(vcs))
        try:
            self._copyright = p.get('copyright', 'long').splitlines()
        except _configparser.NoOptionError:
            pass
        try:
            self._short_copyright = p.get('copyright', 'short').splitlines()
        except _configparser.NoOptionError:
            pass
        try:
            self.with_authors = p.get('files', 'authors')
        except _configparser.NoOptionError:
            pass
        try:
            self.with_files = p.get('files', 'files')
        except _configparser.NoOptionError:
            pass
        try:
            self._ignored_paths = p.get('files', 'ignored')
        except _configparser.NoOptionError:
            pass
        try:
            self._pyfile = p.get('files', 'pyfile')
        except _configparser.NoOptionError:
            pass

    def _info(self):
        return {
            'project': self._name,
            'vcs': self._vcs.name,
            }

    def update_authors(self, dry_run=False):
        _LOG.info('update AUTHORS')
        authors = self._vcs.authors()
        new_contents = u'{} was written by:\n{}\n'.format(
            self._name, u'\n'.join(authors))
        _utils.set_contents('AUTHORS', new_contents, dry_run=dry_run)

    def update_file(self, filename, dry_run=False):
        _LOG.info('update {}'.format(filename))
        contents = _utils.get_contents(filename=filename)
        original_year = self._vcs.original_year(filename=filename)
        authors = self._vcs.authors(filename=filename)
        new_contents = _utils.update_copyright(
            contents=contents, original_year=original_year, authors=authors,
            text=self._copyright, info=self._info(), prefix='# ',
            tag=self._copyright_tag)
        _utils.set_contents(
            filename=filename, contents=new_contents,
            original_contents=contents, dry_run=dry_run)

    def update_files(self, files=None, dry_run=False):
        if files is None or len(files) == 0:
            files = _utils.list_files(root='.')
        for filename in files:
            if self._ignored_file(filename=filename):
                continue
            self.update_file(filename=filename, dry_run=dry_run)

    def update_pyfile(self, dry_run=False):
        if self._pyfile is None:
            _LOG.info('no pyfile location configured, skip `update_pyfile`')
            return
        _LOG.info('update pyfile at {}'.format(self._pyfile))
        current_year = _time.gmtime()[0]
        original_year = self._vcs.original_year()
        authors = self._vcs.authors()
        lines = [
            _utils.copyright_string(
                original_year=original_year, final_year=current_year,
                authors=authors, text=self._copyright, info=self._info(),
                prefix='# '),
            '', 'import textwrap as _textwrap', '', '',
            'LICENSE = """',
            _utils.copyright_string(
                original_year=original_year, final_year=current_year,
                authors=authors, text=self._copyright, info=self._info(),
                prefix=''),
            '""".strip()',
            '',
            'def short_license(info, wrap=True, **kwargs):',
            '    paragraphs = [',
            ]
        paragraphs = _utils.copyright_string(
            original_year=original_year, final_year=current_year,
            authors=authors, text=self._short_copyright, info=self._info(),
            author_format_fn=_utils.short_author_formatter, wrap=False,
            ).split('\n\n')
        for p in paragraphs:
            lines.append("        '{}' % info,".format(
                    p.replace("'", r"\'")))
        lines.extend([
                '        ]',
                '    if wrap:',
                '        for i,p in enumerate(paragraphs):',
                '            paragraphs[i] = _textwrap.fill(p, **kwargs)',
                r"    return '\n\n'.join(paragraphs)",
                '',  # for terminal endline
                ])
        new_contents = '\n'.join(lines)
        _utils.set_contents(
            filename=self._pyfile, contents=new_contents, dry_run=dry_run)

    def _ignored_file(self, filename):
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
        if self._ignored_paths is not None:
            for path in self._ignored_paths:
                if _fnmatch.fnmatch(filename, path):
                    return True
        if self._vcs and not self._vcs.is_versioned(filename):
            return True
        return False
