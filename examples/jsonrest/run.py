
from glashammer import make_app, run_very_simple, render_response

from glashammer.utils import sibpath
from glashammer.utils.json import json_view, JsonRestService

from glashammer.bundles.jquery import setup_jquery


def hello_view(req):
    return render_response('index.jinja')

class HelloService(JsonRestService):

    @json_view
    def get(self, req):
        return {'url':req.url, 'type': 'GET'}

    @json_view
    def post(self, req):
        return {'url':req.url, 'type': 'POST'}

    @json_view
    def put(self, req):
        return {'url':req.url, 'type': 'PUT'}

    @json_view
    def delete(self, req):
        return {'url':req.url, 'type': 'DELETE'}

def setup(app):
    app.add_setup(setup_jquery)

    app.add_template_searchpath(sibpath(__file__, 'templates'))
    app.add_url('/', endpoint='index', view=hello_view)
    app.add_url('/svc', endpoint='service', view=HelloService())

if __name__ == '__main__':
    from os.path import dirname
    app =  make_app(setup, dirname(__file__))
    run_very_simple(app)
