# -*- coding: utf-8 -*-
"""
    glashammer.bundles.forms
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2008 by Glashammer Developers
    :license: MIT
"""

from wtforms import HiddenField

from glashammer.utils import sibpath

class IdField(HiddenField):
    def _value(self):
	    return self.data and unicode(self.data) or u'0'

    def process_formdata(self, valuelist):
        try:
            self.data = int(valuelist[0])
            if self.data == 0:
                self.data = None
        except ValueError:
            self.data = None


def setup_forms(app):
    app.add_template_searchpath(sibpath(__file__, 'templates'))

setup_app = setup_forms


