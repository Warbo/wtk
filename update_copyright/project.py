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

"""Project-specific configuration."""

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
    def __init__(self, root='.', name=None, vcs=None, copyright=None,
                 short_copyright=None):
        self._root = _os_path.normpath(_os_path.abspath(root))
        self._name = name
        self._vcs = vcs
        self._author_hacks = None
        self._year_hacks = None
        self._aliases = None
        self._copyright = None
        self._short_copyright = None
        self.with_authors = False
        self.with_files = False
        self._ignored_paths = None
        self._pyfile = None
        self._encoding = None
        self._width = 79

        # unlikely to occur in the wild :p
        self._copyright_tag = u'-xyz-COPY' + u'-RIGHT-zyx-'

    def load_config(self, stream):
        parser = _configparser.RawConfigParser()
        parser.readfp(stream)
        for section in parser.sections():
            clean_section = section.replace('-', '_')
            try:
                loader = getattr(self, '_load_{}_conf'.format(clean_section))
            except AttributeError, e:
                _LOG.error('invalid {} section'.format(section))
                raise
            loader(parser=parser)

    def _load_project_conf(self, parser):
        try:
            self._name = parser.get('project', 'name')
        except _configparser.NoOptionError:
            pass
        try:
            vcs = parser.get('project', 'vcs')
        except _configparser.NoOptionError:
            pass
        else:
            kwargs = {
                'root': self._root,
                'author_hacks': self._author_hacks,
                'year_hacks': self._year_hacks,
                'aliases': self._aliases,
                }
            if vcs == 'Git':
                self._vcs = _GitBackend(**kwargs)
            elif vcs == 'Bazaar':
                if _BazaarBackend is None:
                    raise _bazaar_import_error
                self._vcs = _BazaarBackend(**kwargs)
            elif vcs == 'Mercurial':
                if _MercurialBackend is None:
                    raise _mercurial_import_error
                self._vcs = _MercurialBackend(**kwargs)
            else:
                raise NotImplementedError('vcs: {}'.format(vcs))

    def _load_copyright_conf(self, parser):
        try:
            self._copyright = parser.get('copyright', 'long').splitlines()
        except _configparser.NoOptionError:
            pass
        try:
            self._short_copyright = parser.get(
                'copyright', 'short').splitlines()
        except _configparser.NoOptionError:
            pass

    def _load_files_conf(self, parser):
        try:
            self.with_authors = parser.get('files', 'authors')
        except _configparser.NoOptionError:
            pass
        try:
            self.with_files = parser.get('files', 'files')
        except _configparser.NoOptionError:
            pass
        try:
            ignored = parser.get('files', 'ignored')
        except _configparser.NoOptionError:
            pass
        else:
            self._ignored_paths = [pth.strip() for pth in ignored.split(',')]
        try:
            pyfile = parser.get('files', 'pyfile')
        except _configparser.NoOptionError:
            pass
        else:
            self._pyfile = _os_path.join(self._root, pyfile)

    def _load_author_hacks_conf(self, parser, encoding=None):
        if encoding is None:
            encoding = self._encoding or _utils.ENCODING
        author_hacks = {}
        for path in parser.options('author-hacks'):
            authors = parser.get('author-hacks', path)
            author_hacks[tuple(path.split('/'))] = set(
                unicode(a.strip(), encoding) for a in authors.split(','))
        self._author_hacks = author_hacks
        if self._vcs is not None:
            self._vcs._author_hacks = self._author_hacks

    def _load_year_hacks_conf(self, parser):
        year_hacks = {}
        for path in parser.options('year-hacks'):
            year = parser.get('year-hacks', path)
            year_hacks[tuple(path.split('/'))] = int(year)
        self._year_hacks = year_hacks
        if self._vcs is not None:
            self._vcs._year_hacks = self._year_hacks

    def _load_aliases_conf(self, parser, encoding=None):
        if encoding is None:
            encoding = self._encoding or _utils.ENCODING
        aliases = {}
        for author in parser.options('aliases'):
            _aliases = parser.get('aliases', author)
            aliases[author] = set(
                unicode(a.strip(), encoding) for a in _aliases.split(','))
        self._aliases = aliases
        if self._vcs is not None:
            self._vcs._aliases = self._aliases

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
        _utils.set_contents(
            _os_path.join(self._root, 'AUTHORS'),
            new_contents, unicode=True, encoding=self._encoding,
            dry_run=dry_run)

    def update_file(self, filename, dry_run=False):
        _LOG.info('update {}'.format(filename))
        contents = _utils.get_contents(
            filename=filename, unicode=True, encoding=self._encoding)
        original_year = self._vcs.original_year(filename=filename)
        authors = self._vcs.authors(filename=filename)
        new_contents = _utils.update_copyright(
            contents=contents, original_year=original_year, authors=authors,
            text=self._copyright, info=self._info(), prefix='# ',
            width=self._width, tag=self._copyright_tag)
        _utils.set_contents(
            filename=filename, contents=new_contents,
            original_contents=contents, unicode=True, encoding=self._encoding,
            dry_run=dry_run)

    def update_files(self, files=None, dry_run=False):
        if files is None or len(files) == 0:
            files = _utils.list_files(root=self._root)
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
                prefix=u'# ', width=self._width),
            u'', u'import textwrap as _textwrap', u'', u'',
            u'LICENSE = """',
            _utils.copyright_string(
                original_year=original_year, final_year=current_year,
                authors=authors, text=self._copyright, info=self._info(),
                prefix=u'', width=self._width),
            u'""".strip()',
            u'',
            u'def short_license(info, wrap=True, **kwargs):',
            u'    paragraphs = [',
            ]
        paragraphs = _utils.copyright_string(
            original_year=original_year, final_year=current_year,
            authors=authors, text=self._short_copyright, info=self._info(),
            author_format_fn=_utils.short_author_formatter, wrap=False,
            ).split(u'\n\n')
        for p in paragraphs:
            lines.append(u"        '{}' % info,".format(
                    p.replace(u"'", ur"\'")))
        lines.extend([
                u'        ]',
                u'    if wrap:',
                u'        for i,p in enumerate(paragraphs):',
                u'            paragraphs[i] = _textwrap.fill(p, **kwargs)',
                ur"    return '\n\n'.join(paragraphs)",
                u'',  # for terminal endline
                ])
        new_contents = u'\n'.join(lines)
        _utils.set_contents(
            filename=self._pyfile, contents=new_contents, unicode=True,
            encoding=self._encoding, dry_run=dry_run)

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
        filename = _os_path.relpath(filename, self._root)
        if self._ignored_paths is not None:
            for path in self._ignored_paths:
                if _fnmatch.fnmatch(filename, path):
                    _LOG.debug('ignoring {} (matched {})'.format(
                            filename, path))
                    return True
        if self._vcs and not self._vcs.is_versioned(filename):
            _LOG.debug('ignoring {} (not versioned))'.format(filename))
            return True
        return False
