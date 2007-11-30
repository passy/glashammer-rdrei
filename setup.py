"""
Setup script for Glashammer.
"""

from distutils.core import setup


setup(

    name='Glashammer',


    packages = [
        'glashammer'
    ],

    package_dir = {
        'glashammer': 'glashammer'
    },

    package_data = {
        'glashammer': [
            '*_public/*/*',
            '*_templates/*'
        ]
    },
)
