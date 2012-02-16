#!/usr/bin/env python
#
# Copyright

"""Update copyright information with information from the VCS repository.

Run from the project's repository root.

Replaces every line starting with ``^# Copyright`` and continuing with
``^#`` with an auto-generated copyright blurb.  If you want to add
``#``-commented material after a copyright blurb, please insert a blank
line between the blurb and your comment, so the next run of
``update_copyright.py`` doesn't clobber your comment.

If no files are given, a list of files to update is generated
automatically.
"""

import logging as _logging

from update_copyright import LOG as _LOG
from update_copyright.project import Project


if __name__ == '__main__':
    import optparse
    import sys

    usage = "%%prog [options] [file ...]"

    p = optparse.OptionParser(usage=usage, description=__doc__)
    p.add_option('--config', dest='config', default='.update-copyright.conf',
                 metavar='PATH', help='path to project config file (%default)')
    p.add_option('--no-authors', dest='authors', default=True,
                 action='store_false', help="Don't generate AUTHORS")
    p.add_option('--no-files', dest='files', default=True,
                 action='store_false', help="Don't update file copyrights")
    p.add_option('--no-pyfile', dest='pyfile', default=True,
                 action='store_false', help="Don't update the pyfile")
    p.add_option('--dry-run', dest='dry_run', default=False,
                 action='store_true', help="Don't make any changes")
    p.add_option('-v', '--verbose', dest='verbose', default=0,
                 action='count', help='Increment verbosity')
    options,args = p.parse_args()

    _LOG.setLevel(max(0, _logging.ERROR - 10*options.verbose))

    project = Project()
    project.load_config(open(options.config, 'r'))
    if options.authors:
        project.update_authors(dry_run=options.dry_run)
    if options.files:
        project.update_files(files=args, dry_run=options.dry_run)
    if options.pyfile:
        project.update_pyfile(dry_run=options.dry_run)