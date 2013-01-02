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

"""Tools for setting up a package logging.

This module is separate from `tools` to avoid module dependency
cycles.  This module has no internal dependencies, while `tools`
depends on many of the other modules.  With this module separate, the
other internal modules have access to the default logger before the
package configuration is built up enough to configure it according to
your external specifications.
"""

import logging as _logging


def get_basic_logger(name, level=_logging.WARN):
    """Create and return a basic logger

    This utility function encapsulates a bunch of `logging`
    boilerplate that I use in several packages.
    """
    log = _logging.getLogger(name)
    log.setLevel(level)
    formatter = _logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler = _logging.StreamHandler()
    stream_handler.setLevel(_logging.DEBUG)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    # Cache handlers for easy swapping depending on config settings
    log._handler_cache = {'stream': stream_handler}
    return log
