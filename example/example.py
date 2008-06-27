
from os.path import dirname

from glashammer.application import make_app, run_very_simple, render_response

FOLDER = dirname(__file__)

def index_view(req):
    return render_response('hello.jinja')

def setup(app):
    app.add_url_rule('/', 'example/hello', view=index_view)
    app.add_template_searchpath(FOLDER)

if __name__ == '__main__':
    app = make_app(setup, FOLDER)
    run_very_simple(app)


