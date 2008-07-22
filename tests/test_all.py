
import os, shutil

from nose.tools import assert_raises

from werkzeug.test import Client

from glashammer.application import GlashammerApplication
from glashammer.utils import render_response, Response, local, \
    render_template, sibpath, get_request, get_app

from glashammer.bundles.json import json_view, JsonRestService

def make_app(setup_func, instance_dir=None):
    return GlashammerApplication(setup_func, instance_dir)



# Basics

def _setup_empty(app):
    return


def test_make_app():
    app = make_app(_setup_empty, 'test_output')


def test_app_no_instance():
    """
    Test creating an application with no instance directory
    """
    app = make_app(_setup_empty)


def test_app_missing_instance():
    """
    Explicitly passed application directories must exist.
    """
    assert_raises((RuntimeError,), make_app, _setup_empty, 'i_do_not_exist')


# Setup functions

def _add_first_setup(app):
    app.add_setup(_add_second_setup)

def _add_second_setup(app):
    app.test_var = 1


def test_add_setup_func():
    """
    Adding a setup function and make sure it's called
    """
    app = make_app(_add_first_setup, 'test_output')
    assert app.test_var == 1


# View and endpoints

def _has_rule(map, url, endpoint):
    """
    Check a map contains a url for an endpoint
    """
    return (url, endpoint) in [(i.rule, i.endpoint) for i in map.iter_rules()]


def test_add_rule():
    """
    Adding a rule, and that it's in the map
    """
    def _add_rule_setup(app):
        app.add_url('/', endpoint='foo/blah')
    app = make_app(_add_rule_setup, 'test_output')
    assert _has_rule(app.map, '/', 'foo/blah')

def _aview(req):
    return 1

def _a_real_view(req):
    return Response('hello')


def test_add_view():
    """
    Adding a rule, endpoint and view, and that it's called.
    """
    def _add_view_setup(app):
        app.add_url('/', endpoint='foo/blah', view=_aview)
    app = make_app(_add_view_setup, 'test_output')
    assert _has_rule(app.map, '/', 'foo/blah')
    assert app.get_view(None, 'foo/blah', {}) == 1


class _Controller(object):

    def index(self, req):
        return 3

    def edit(self, req):
        return 2


def test_add_controller():
    """
    Add a controller and check the views.
    """
    def _add_controller(app):
        app.add_url('/index', 'foo/index')
        app.add_url('/edit', 'foo/edit')

        c = _Controller()
        app.add_views_controller('foo', c)

    app = make_app(_add_controller, 'test_output')

    # duplicated, but it's all good
    assert _has_rule(app.map, '/index', 'foo/index')
    assert _has_rule(app.map, '/edit', 'foo/edit')

    # Now for the real ones
    assert app.get_view(None, 'foo/index', {}) == 3
    assert app.get_view(None, 'foo/edit', {}) == 2


# Templating

class TestTemplating(object):

    def setup(self):
        try:
            shutil.rmtree('test_output/templates')
        except OSError:
            pass
        os.mkdir('test_output/templates')
        f = open('test_output/templates/hello.html', 'w')
        f.write('hello')
        f.close()
        f = open('test_output/templates/variables.html', 'w')
        f.write('{{ hello }}')
        f.close()

    def teardown(self):
        shutil.rmtree('test_output/templates')

    def test_add_template_searchpath(self):
        """
        Add a template search path
        """
        def _add_template_searchpath(app):
            app.add_template_searchpath('test_output/templates')

        app = make_app(_add_template_searchpath, 'test_output')
        assert app.template_env.get_template('hello.html').render() == 'hello'

    def test_add_template_global(self):
        """
        Add a template global and ensure it is available for rendering
        """

        def _add_template_global(app):
            app.add_template_global('hello', 'byebye')
            app.add_template_searchpath('test_output/templates')

        app = make_app(_add_template_global, 'test_output')
        assert app.template_env.get_template('variables.html').render() == 'byebye'

    def test_render_template(self):
        """
        Test a template render
        """
        def _add_bits(app):
            app.add_template_searchpath('test_output/templates')

        app = make_app(_add_bits, 'test_output')

        s = render_template('variables.html', hello='byebye')

        assert s == 'byebye'


    def test_render_response(self):
        """
        Test a full response.
        """

        def _simple_view(req):
            return render_response('variables.html', hello='byebye')

        def _add_bits(app):
            app.add_template_searchpath('test_output/templates')
            app.add_url('/', 'foo/blah', _simple_view)

        app = make_app(_add_bits, 'test_output')
        c = Client(app)
        i, status, headers = c.open()
        assert list(i) == ['byebye']
        assert status == '200 OK'

# Grabbing local variable

class TestLocals():

    def _a_view(req):
        assert req is local.request
        return Response('hello')

    def _setup_view(app):
        app.add_url('/', '', view=_a_view)

    def setup(self):
        self.app = make_app(_setup_app, 'test_output')
        self.client = Client(app)

    def test_get_app(self):
        assert get_app() is self.app

    def test_get_req(self):
        a, s, h = self.client.open()
        assert s == '200 OK'

# config

def test_add_config():

    def _setup_config(app):
        app.add_config_var('foo', str, 'blah')

    app = make_app(_setup_config, 'test_output')
    assert app.conf['foo'] == 'blah'

# processors

def test_req_processor():

    def _a_view(req):
        return Response('%s' % (req.foo == 1))

    def _process_request(req):
        req.foo = 1

    def _setup_proc(app):
        app.add_request_processor(_process_request)
        app.add_url('/', '', view=_a_view)

    app = make_app(_setup_proc, 'test_output')
    c = Client(app)

    appiter, status, headers = c.open()

    assert list(appiter)[0] == 'True'

def test_resp_processor():

    def _a_view(req):
        return Response('hello')

    def _process_response(resp):
        resp.data = 'byebye'

    def _setup_proc(app):
        app.add_response_processor(_process_response)
        app.add_url('/', '', view=_a_view)

    app = make_app(_setup_proc, 'test_output')
    c = Client(app)

    appiter, status, headers = c.open()

    assert list(appiter)[0] == 'byebye'

def test_local_processor():

    def _a_view(req):
        return Response('%s' % (local.foo == 1))

    def _local_proc(local):
        local.foo = 1

    def _setup_local(app):
        app.add_local_processor(_local_proc)
        app.add_url('/', '', view=_a_view)

    app = make_app(_setup_local, 'test_output')

    c = Client(app)
    appiter, status, headers = c.open()
    assert list(appiter)[0] == 'True'



# Sessions
def _sessioned_view(req):
    assert local.session == {}
    return Response('')

def test_session_setup():

    def _setup_sessions(app):
        from glashammer.bundles.sessions import setup_app
        app.add_setup(setup_app)

        app.add_url('/', '', view=_sessioned_view)

    app = make_app(_setup_sessions, 'test_output')

    c = Client(app)
    c.open()


# Html Helpers

def test_htmlhelpers_setup():

    def _setup_helpers(app):
        from glashammer.bundles.htmlhelpers import setup_app
        app.add_setup(setup_app)

    app = make_app(_setup_helpers, 'test_output')
    assert 'h' in app.template_env.globals

    # now test you can actually use the thing
    h = app.template_env.globals['h']
    assert h.meta() == '<meta>'

# Json Stuff

def test_json_response():

    @json_view
    def _a_json_view(req):
        return {'foo': 'blah'}

    def _setup_json(app):
        app.add_url('/', '', view=_a_json_view)

    app = make_app(_setup_json, 'test_output')

    c = Client(app)
    appiter, status, headers = c.open()

    s = list(appiter)[0]

    h = dict(headers)
    assert 'text/javascript' in h['Content-Type']
    assert s == '{"foo": "blah"}'


class _Service(JsonRestService):

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


class TestJsonRestService(object):

    def setup(self):
        def _setup_json(app):
            app.add_url('/', '', view=_Service())

        app = make_app(_setup_json, 'test_output')

        self.client = Client(app)

    def test_get(self):
        ai, st, h = self.client.open(method='GET')
        s = list(ai)[0]
        assert 'GET' in s

    def test_post(self):
        ai, st, h = self.client.open(method='POST')
        s = list(ai)[0]
        assert 'POST' in s

    def test_put(self):
        ai, st, h = self.client.open(method='PUT')
        s = list(ai)[0]
        assert 'PUT' in s

    def test_delete(self):
        ai, st, h = self.client.open(method='DELETE')
        s = list(ai)[0]
        assert 'DELETE' in s

# file utilities

def test_sibpath():
    assert sibpath('foo', 'blah') == 'blah'
    assert sibpath('/foo/boo', 'blah') == '/foo/blah'


