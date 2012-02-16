# Copyright

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
