# Copyright

"""Automatically update copyright boilerplate.

This package is adapted from a script written for `Bugs
Everywhere`_. and later modified for `Hooke`_ before returning to
`Bugs Everywhere`_.  I finally gave up on maintaining separate
versions, so here it is as a stand-alone package.

.. _Bugs Everywhere: http://bugseverywhere.org/
.. _Hooke: http://code.google.com/p/hooke/
"""

from .log import get_basic_logger as _get_basic_logger


__version__ = '0.2'


LOG = _get_basic_logger(name='update-copyright')
