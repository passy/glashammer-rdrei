# -*- coding: utf-8 -*-
"""
    glashammer.bundles.forms
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2008 by Glashammer Developers
    :license: MIT
"""


from glashammer.utils import sibpath


def setup_forms(app):
    app.add_template_searchpath(sibpath(__file__, 'templates'))

setup_app = setup_forms


