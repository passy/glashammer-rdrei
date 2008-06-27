
from os.path import dirname

from gh.application import make_app, run_very_simple, render_response

from werkzeug import Response

def index_view(req):
    #return Response(u'Hello World')
    return render_response('hello.jinja')

def setup(app):
    app.add_url_rule('/', 'example/hello', view=index_view)
    app.add_template_searchpath(dirname(__file__))

if __name__ == '__main__':
    app = make_app(setup, dirname(__file__))
    run_very_simple(app)


