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

from __future__ import absolute_import

import io as _io
import os as _os
import sys as _sys

import mercurial as _mercurial
from mercurial.__version__ import version as _version
import mercurial.dispatch as _mercurial_dispatch

from . import VCSBackend as _VCSBackend
from . import utils as _utils


class MercurialBackend (_VCSBackend):
    name = 'Mercurial'

    def __init__(self, **kwargs):
        super(MercurialBackend, self).__init__(**kwargs)
        self._version = _version

    def _hg_cmd(*args):
        cwd = _os.getcwd()
        stdout = _sys.stdout
        stderr = _sys.stderr
        tmp_stdout = _io.StringIO()
        tmp_stderr = _io.StringIO()
        _sys.stdout = tmp_stdout
        _sys.stderr = tmp_stderr
        _os.chdir(self._root)
        try:
            _mercurial_dispatch.dispatch(list(args))
        finally:
            _os.chdir(cwd)
            _sys.stdout = stdout
            _sys.stderr = stderr
        return (tmp_stdout.getvalue().rstrip('\n'),
                tmp_stderr.getvalue().rstrip('\n'))

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
