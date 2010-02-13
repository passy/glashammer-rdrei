# -*- coding: utf-8 -*-
"""
helloworld_i18n
~~~~~~~~~~~~~~~

"Hello World!" application with i18n support.

:copyright: 2010, The Glashammer Authors
:license: MIT
"""

from glashammer.application import make_app
from glashammer.bundles.i18n import setup_i18n, _
from glashammer.bundles.i18n.request import I18NRequestMixin
from glashammer.bundles.sessions import setup_sessions
from glashammer.utils import run_very_simple, Response
from glashammer.utils.wrappers import Request as _Request

from os.path import dirname, join


def hello_view(req):
    # NOTE: A comment for the translator.
    message = _("Hello World!")
    return Response('<h1>%s</h1>' % message)

# Add the i18n mixin
class Request(_Request, I18NRequestMixin):
    pass

def setup(app):
    app.add_setup(setup_sessions)
    app.add_setup(setup_i18n, join(dirname(__file__), "i18n"))
    app.add_url('/', endpoint='hello/index', view=hello_view)


# Used by gh-admin
def create_app():
    return make_app(setup, dirname(__file__),
                   request_cls=Request)

if __name__ == '__main__':
    app = create_app()
    run_very_simple(app)
