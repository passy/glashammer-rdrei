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

from setuptools import setup, find_packages
from glashammer.version import glashammer_version


setup(

    # Required metadata
    name='Glashammer',
    version=glashammer_version,

    # Scripts
    scripts=['bin/gh-admin'],
    # package information
    packages=find_packages(exclude=['tests']),

    package_dir={
        'glashammer': 'glashammer',
    },

    # this is terrible
    package_data={
        'glashammer': [
            'shared/jquery/*',
            'templates/*'
        ],
        'glashammer.bundles.depracated.auth': [
            'templates/*',
        ],
        'glashammer.bundles.jquery': [
            'templates/includes/*'
        ],
        'glashammer.bundles.forms': [
            'templates/macros/*',
        ],
        'glashammer.appliances.admin': [
            'templates/_admin/*', 'shared/*',
        ]
    },

    install_requires=[
        'werkzeug', 'jinja2', 'flatland', 'sanescript',
    ],

    # Additional pypi metadata
    description='Full stack web framework',

    long_description=__doc__,

    url='http://glashammer.org',

    author='Ali Afshar',
    author_email='aafshar@gmail.com',

    classifiers=[
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development']
    )
