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

"""Automatically update copyright boilerplate.

This package is adapted from a script written for `Bugs
Everywhere`_. and later modified for `Hooke`_ before returning to
`Bugs Everywhere`_.  I finally gave up on maintaining separate
versions, so here it is as a stand-alone package.

.. _Bugs Everywhere: http://bugseverywhere.org/
.. _Hooke: http://code.google.com/p/hooke/
"""

from .log import get_basic_logger as _get_basic_logger


__version__ = '0.6'


LOG = _get_basic_logger(name='update-copyright')
