"""
Setup script for Glashammer.
"""

from distutils.core import setup


setup(
    name='Glashammer',

    version='0.1',

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
)
