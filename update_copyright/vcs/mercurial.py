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

from . import VCSBackend as _VCSBackend
from . import utils as _utils


class MercurialBackend (_VCSBackend):
    name = 'Mercurial'

    def __init__(self, **kwargs):
        super(MercurialBackend, self).__init__(**kwargs)
        self._version = _version

    def _hg_cmd(*args):
        status,stdout,stderr = _utils.invoke(
            ['hg'] + list(args), cwd=self._root, unicode_output=True)
        return stdout.rstrip('\n')

    def _years(self, filename=None):
        args = [
            '--template', '{date|shortdate}\n',
            # shortdate filter: YEAR-MONTH-DAY
            ]
        if filename is not None:
            args.extend(['--follow', filename])
        output,error = mercurial_cmd('log', *args)
        years = set(int(line.split('-', 1)[0]) for line in output.splitlines())
        return years

    def _authors(self, filename=None):
        args = ['--template', '{author}\n']
        if filename is not None:
            args.extend(['--follow', filename])
        output,error = mercurial_cmd('log', *args)
        authors = set(output.splitlines())
        return authors

    def is_versioned(self, filename):
        output,error = mercurial_cmd('log', '--follow', filename)
        if len(error) > 0:
            return False
        return True
