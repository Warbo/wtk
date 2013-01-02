#!/usr/bin/env python
#
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

"""Update copyright information with information from the VCS repository.

Run from the project's repository root.

Replaces every line starting with ``^# Copyright`` and continuing with
``^#`` with an auto-generated copyright blurb.  If you want to add
``#``-commented material after a copyright blurb, please insert a blank
line between the blurb and your comment, so the next run of
``update_copyright.py`` doesn't clobber your comment.

You should configure this program via an ``.update-copyright.conf``
file in your project root.
"""

import logging as _logging
import os.path as _os_path

from update_copyright import __version__
from update_copyright import LOG as _LOG
from update_copyright.project import Project


if __name__ == '__main__':
    import argparse
    import sys

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        '--version', action='version',
        version='%(prog)s {}'.format(__version__))
    p.add_argument(
        '--config', dest='config', default='.update-copyright.conf',
        metavar='PATH', help='path to project config file')
    p.add_argument(
        '--no-authors', dest='authors', default=True, action='store_const',
        const=False, help="Don't generate AUTHORS")
    p.add_argument(
        '--no-files', dest='files', default=True, action='store_const',
        const=False, help="Don't update file copyrights")
    p.add_argument(
        '--no-pyfile', dest='pyfile', default=True, action='store_const',
        const=False, help="Don't update the pyfile")
    p.add_argument(
        '--dry-run', dest='dry_run', default=False, action='store_const',
        const=True, help="Don't make any changes")
    p.add_argument(
        '-v', '--verbose', dest='verbose', default=0, action='count',
        help='Increment verbosity')
    p.add_argument(
        'file', nargs='*',
        help=(
            'Explicitly select files to update (otherwise update the whole '
            'project)'))

    args = p.parse_args()

    _LOG.setLevel(max(_logging.DEBUG, _logging.ERROR - 10*args.verbose))

    project = Project(root=_os_path.dirname(_os_path.abspath(args.config)))
    project.load_config(open(args.config, 'r'))
    if args.authors and project.with_authors:
        project.update_authors(dry_run=args.dry_run)
    if args.files and project.with_files:
        project.update_files(files=args.file, dry_run=args.dry_run)
    if args.pyfile and project._pyfile:
        project.update_pyfile(dry_run=args.dry_run)
