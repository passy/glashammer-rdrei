
from os.path import dirname

from glashammer import make_app, run_very_simple, render_response

FOLDER = dirname(__file__)

def index_view(req):
    return render_response('hello.jinja')

def setup(app):
    app.add_url('/', 'example/hello', view=index_view)
    app.add_template_searchpath(FOLDER)

def signal(*args):
    print 'signal-args', args

if __name__ == '__main__':
    app = make_app(setup, FOLDER)
    run_very_simple(app)


