
from os.path import dirname

from glashammer.application import make_app

from glashammer.utils import sibpath, run_very_simple, render_response
from glashammer.utils.json import json_view, JsonRestService

from glashammer.bundles.jquery import setup_jquery


def hello_view(req):
    return render_response('index.jinja')

class HelloService(JsonRestService):

    def get(self, req):
        return {'url':req.url, 'type': 'GET'}

    def post(self, req):
        return {'url':req.url, 'type': 'POST'}

    def put(self, req):
        return {'url':req.url, 'type': 'PUT'}

    def delete(self, req):
        return {'url':req.url, 'type': 'DELETE'}

def setup(app):
    app.add_setup(setup_jquery)

    app.add_template_searchpath(sibpath(__file__, 'templates'))
    app.add_url('/', endpoint='index', view=hello_view)
    app.add_url('/svc', endpoint='service', view=HelloService())

# Used by gh-admin
def create_app():
    return make_app(setup, dirname(__file__))

if __name__ == '__main__':
    app =  create_app()
    run_very_simple(app)
