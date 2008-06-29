

from glashammer import make_app, run_very_simple, Response


def hello_view(req):
    return Response('<h1>Hello World</h1>')

def setup(app):
    app.add_url('/', endpoint='hello/index', view=hello_view)

if __name__ == '__main__':
    from os.path import dirname
    app =  make_app(setup, dirname(__file__))
    run_very_simple(app)
