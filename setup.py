"""
Setup script for Glashammer.
"""

from distutils.core import setup


setup(
    name='Glashammer',

    version='0.1',

    packages = [
        'glashammer', 'glashammer.bundles', 'glashammer.bundles.auth',
        'glashammer.bundles.admin',
    ],

    package_dir = {
        'glashammer': 'glashammer'
    },

    package_data = {
        'glashammer': [
            'shared/*',
            'templates/macros/forms.html',
            'templates/*.html'
        ]
    },
)
