# Copyright (C) 2012 W. Trevor King <wking@drexel.edu>

"Automatically update copyright blurbs in versioned source."

from distutils.core import setup as _setup
import os.path as _os_path

from update_copyright import __version__


classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Operating System :: OS Independent
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Software Development
"""

_this_dir = _os_path.dirname(__file__)

_setup(
    name='update-copyright',
    version=__version__,
    maintainer='W. Trevor King',
    maintainer_email='wking@drexel.edu',
    url='http://tremily.us/posts/update-copyright/',
    download_url='http://physics.drexel.edu/~wking/code/git/gitweb.cgi?p=update-copyright.git;a=snapshot;h=v{};sf=tgz'.format(__version__),
    license = 'GNU General Public License (GPL)',
    platforms = ['all'],
    description = __doc__,
    long_description=open(_os_path.join(_this_dir, 'README'), 'r').read(),
    classifiers = filter(None, classifiers.split('\n')),
    scripts = ['bin/update-copyright.py'],
    packages = ['update_copyright', 'update_copyright.vcs'],
    provides = ['update_copyright', 'update_copyright.vcs'],
    )
