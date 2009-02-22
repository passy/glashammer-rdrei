# -*- coding: utf-8 -*-
from os.path import dirname

from glashammer.application import make_app
from glashammer.utils import run_very_simple, sibpath

from glashammer.bundles.couchdbdb import setup_couchdb

TEMPLATES_DIRECTORY = sibpath(__file__, 'templates')
SHARED_DIRECTORY = sibpath(__file__, 'shared')

# Main application setup
def setup(app):
    app.add_template_searchpath(TEMPLATES_DIRECTORY)
    app.add_shared('main', SHARED_DIRECTORY)

    app.add_setup(setup_couchdb)

# Hook for gh-admin
def create_app():
    app =  make_app(setup, dirname(__file__))
    return app

if __name__ == '__main__':
    app = create_app()
    run_very_simple(app)

