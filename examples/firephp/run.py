

from os.path import dirname

from glashammer.application import make_app
from glashammer.utils import run_very_simple, Response


def hello_view(req):
    return Response('<h1>Hello World</h1>')

def setup(app):
    app.add_url('/', endpoint='hello/index', view=hello_view)

    from glashammer.bundles.firephp import setup_app
    app.add_setup(setup_app)

def create_app():
    app =  make_app(setup, dirname(__file__))
    return app

if __name__ == '__main__':
    app = create_app()
    run_very_simple(app)
