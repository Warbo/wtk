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

import StringIO as _StringIO

import bzrlib as _bzrlib
import bzrlib.builtins as _bzrlib_builtins
import bzrlib.log as _bzrlib_log

from . import VCSBackend as _VCSBackend


class _LogFormatter (_bzrlib_log.LogFormatter):
    supports_merge_revisions = True
    preferred_levels = 0
    supports_deta = False
    supports_tags = False
    supports_diff = False

    def log_revision(self, revision):
        raise NotImplementedError


class _YearLogFormatter (_LogFormatter):
    def log_revision(self, revision):
        self.to_file.write(
            time.strftime('%Y', time.gmtime(revision.rev.timestamp))
            +'\n')


class _AuthorLogFormatter (_LogFormatter):
    def log_revision(self, revision):
        authors = revision.rev.get_apparent_authors()
        self.to_file.write('\n'.join(authors)+'\n')


class BazaarBackend (_VCSBackend):
    name = 'Bazaar'

    def __init__(self, **kwargs):
        super(BazaarBackend, self).__init__(**kwargs)
        self._version = _bzrlib.__version__

    def _years(self, filename=None):
        cmd = _bzrlib_builtins.cmd_log()
        cmd.outf = _StringIO.StringIO()
        kwargs = {'log_format':_YearLogFormatter, 'levels':0}
        if filename is not None:
            kwargs['file_list'] = [filename]
        cmd.run(**kwargs)
        years = set(int(year) for year in cmd.outf.getvalue().splitlines())
        return years

    def _authors(self, filename=None):
        cmd = _bzrlib_builtins.cmd_log()
        cmd.outf = _StringIO.StringIO()
        kwargs = {'log_format':_AuthorLogFormatter, 'levels':0}
        if filename is not None:
            kwargs['file_list'] = [filename]
        cmd.run(**kwargs)
        authors = set(cmd.outf.getvalue().splitlines())
        return authors

    def is_versioned(self, filename):
        cmd = _bzrlib_builtins.cmd_log()
        cmd.outf = StringIO.StringIO()
        cmd.run(file_list=[filename])
        return True
