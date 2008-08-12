# -*- coding: utf-8 -*-
import transaction

from os.path import dirname

from glashammer import make_app, run_very_simple, sibpath, Response

from glashammer.bundles.ZODBdb import setup_zodb, get_zodb_root

class Fruit(object):
    pass

def index_view(req):
    root = get_zodb_root()
    root[len(root)] = Fruit()
    transaction.commit()
    return Response('Hello World: %s fruits' % len(root))

# Main application setup
def setup(app):
    app.add_setup(setup_zodb)
    app.add_url('/', 'index', view=index_view)

# Hook for gh-admin
def create_app():
    app =  make_app(setup, dirname(__file__))
    return app

if __name__ == '__main__':
    app = create_app()
    run_very_simple(app)

