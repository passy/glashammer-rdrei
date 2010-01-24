from glashammer.application import make_app
from glashammer.utils import run_very_simple, Response

from os.path import dirname


def hello_view(req):
    return Response('<h1>Hello World</h1>')


def setup(app):
    app.add_url('/', endpoint='hello/index', view=hello_view)


# Used by gh-admin
def create_app():
    return make_app(setup, dirname(__file__))


if __name__ == '__main__':
    app = make_app(setup)
    run_very_simple(app)
