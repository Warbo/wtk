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

"Automatically update copyright blurbs in versioned source."

import codecs as _codecs
from distutils.core import setup as _setup
import os.path as _os_path

from update_copyright import __version__


_this_dir = _os_path.dirname(__file__)

_setup(
    name='update-copyright',
    version=__version__,
    maintainer='W. Trevor King',
    maintainer_email='wking@tremily.us',
    url='http://blog.tremily.us/posts/update-copyright/',
    download_url='http://git.tremily.us/?p=update-copyright.git;a=snapshot;h=v{};sf=tgz'.format(__version__),
    license = 'GNU General Public License (GPL)',
    platforms = ['all'],
    description = __doc__,
    long_description=_codecs.open(
        _os_path.join(_this_dir, 'README'), 'r', encoding='utf-8').read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        ],
    scripts = ['bin/update-copyright.py'],
    packages = ['update_copyright', 'update_copyright.vcs'],
    provides = ['update_copyright', 'update_copyright.vcs'],
    )
