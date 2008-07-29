"""
Setup script for Glashammer.
"""

from distutils.core import setup


setup(

    # Required metadata
    name='Glashammer',
    version='0.1',

    # package information
    packages = [
        'glashammer', 'glashammer.bundles', 'glashammer.bundles.auth',
        'glashammer.bundles.forms', 'glashammer.bundles.i18n',
        'glashammer.bundles.jquery', 'glashammer.utils'
    ],

    package_dir = {
        'glashammer': 'glashammer'
    },

    package_data = {
        'glashammer': [
            'shared/jquery/*',
            'bundles/auth/templates/*',
            'bundles/forms/templates/macros/forms.html',
            'bundles/jquery/templates/includes/*'
            'templates/*.html'
        ]
    },

    # Additional pypi metadata
    description = 'Full stack web framework',

    long_description = ('Glashammer is a Python web framework with an emphasis'
    ' on simplicity, flexibility, and extensibility. It is built atop excellent'
    ' components and reinvents zero wheels.'),

    url = 'http://glashammer.welterde.de',

    author='Ali Afshar',
    author_email='aafshar@gmail.com',

    classifiers=[
          'Development Status :: 4 - Beta',
    ]
)
