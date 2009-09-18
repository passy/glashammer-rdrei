"""
Glashammer
==========

Glashammer is a Python web framework with an emphasis
on simplicity, flexibility, and extensibility. It is built atop excellent
components and reinvents zero wheels.

The `Glashammer tip
<http://bitbucket.org/aafshar/glashammer-main/get/tip.zip#egg=Glashammer-dev>`_ is
installable via ``easy_install Glashammer==dev``
"""

from distutils.core import setup

from glashammer.version import glashammer_version


setup(

    # Required metadata
    name='Glashammer',
    version=glashammer_version,

    # Scripts
    scripts = ['bin/gh-admin'],
    # package information
    packages = [
        'glashammer',
        'glashammer.utils',
        'glashammer.tools',
        'glashammer.bundles',
        'glashammer.bundles.forms',
        'glashammer.bundles.i18n',
        'glashammer.bundles.jquery',
        'glashammer.bundles.depracated',
        'glashammer.bundles.depracated.auth',
        'glashammer.bundles.contrib.db',
        'glashammer.bundles.contrib.auth',
        'glashammer.bundles.contrib.dev',
    ],

    package_dir = {
        'glashammer': 'glashammer',
    },

    package_data = {
        'glashammer': [
            'shared/jquery/*',
            'templates/*'
        ],
        'glashammer.bundles.auth' : [
            'templates/*',
        ],
        'glashammer.bundles.jquery': [
            'templates/includes/*'
        ],
        'glashammer.bundles.forms' : [
            'templates/macros/*',
        ]
    },

    # Additional pypi metadata
    description = 'Full stack web framework',

    long_description = __doc__,

    url = 'http://glashammer.org',

    author='Ali Afshar',
    author_email='aafshar@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
    ]
)
