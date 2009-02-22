
import os, shutil, urlparse

from datetime import datetime, date, time

from nose.tools import assert_raises

from werkzeug.test import Client

from glashammer.application import GlashammerApplication, make_app
from glashammer.utils import render_response, Response, local, \
    render_template, sibpath, get_request, get_app, url_for, \
    gen_pwhash, check_pwhash, Configuration

from glashammer.utils.http import redirect, redirect_to

from glashammer.utils.json import json_view, JsonRestService

from glashammer.bundles import i18n



def test_make_app():
    make_app(lambda a: None)

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


def _test_finalized():

    def _bview(req):
        app = get_app()
        assert_raises((RuntimeError,), app.add_config_var, 'a', str, 'a')
        return Response('hello')

    def _setup_app(app):
        app.add_url('/', 'hoo', _bview)

    app = make_app(_setup_app, 'test_output')

    c = Client(app)
    c.open()



# Setup functions

def _add_first_setup(app):
    app.add_setup(_add_second_setup)
    app.called = 0

def _add_second_setup(app, banana=1):
    app.test_var = banana
    app.called += 1


def test_add_setup_func():
    """
    Adding a setup function and make sure it's called
    """
    app = make_app(_add_first_setup, 'test_output')
    assert app.test_var == 1


def _add_first_setup_with_args(app):
    app.add_setup(_add_second_setup, 2)
    app.called = 0

def test_add_setup_func_args():
    app = make_app(_add_first_setup_with_args, 'test_output')
    assert app.test_var == 2

def _add_first_setup_twice(app):
    app.add_setup(_add_second_setup)
    app.add_setup(_add_second_setup)
    app.called = 0

def test_add_setup_func_twice():
    app = make_app(_add_first_setup_twice, 'test_output')
    assert app.called == 1

def _add_first_setup_twice_with_diff_args(app):
    app.add_setup(_add_second_setup, 1)
    app.add_setup(_add_second_setup, 2)
    app.called = 0

def test_add_setup_func_twice_with_diff_args():
    app = make_app(_add_first_setup_twice_with_diff_args, 'test_output')
    assert app.called == 2


def _add_first_setup_twice_with_same_args(app):
    app.add_setup(_add_second_setup, 1)
    app.add_setup(_add_second_setup, 1)
    app.called = 0

def test_add_setup_func_twice_with_diff_args():
    app = make_app(_add_first_setup_twice_with_same_args, 'test_output')
    assert app.called == 1


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

def test_endpoint_lookup():
    """
    Adding a rule, and that it's in the map
    """
    def _add_rule_setup(app):
        app.add_url('/', endpoint='foo/blah')

    app = make_app(_add_rule_setup, 'test_output')

    assert url_for('foo/blah') == '/'

def test_add_rule():
    def _add_rule_setup(app):
        from werkzeug.routing import Rule
        r = Rule('/', endpoint='ep')
        app.add_url_rule(r, view=_aview)

    app = make_app(_add_rule_setup, 'test_output')

    assert _has_rule(app.map, '/', 'ep')
    assert app.get_view(None, 'ep', {}) == 1


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
        f = open('test_output/templates/events.html', 'w')
        f.write('{{ emit_event("anevent") }}')
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
    
    def test_add_template_tests(self):
        """
        Add template tests and ensure they are available for rendering
        """
        def _template_test(n):
            return True
        
        def _add_template_tests(app):
            app.add_template_test('asdf', _template_test)
            app.add_template_searchpath('test_output/templates')
        
        app = make_app(_add_template_tests, 'test_output')
        assert app.template_env.tests['asdf'] == _template_test

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

    def test_template_emit(self):
        emitted = []

        def _simple_view(req):
            return render_response('events.html')

        def _on_blah():
            emitted.append('anevent')

        def _add_bits(app):
            app.add_template_searchpath('test_output/templates')
            app.connect_event('anevent', _on_blah)
            app.add_url('/', 'foo/blah', _simple_view)

        app = make_app(_add_bits, 'test_output')
        c = Client(app)
        i, status, headers = c.open()
        assert emitted == ['anevent']


# Grabbing local variable

class TestLocals():


    def setup(self):

        def _a_view(req):
            assert req is local.request
            return Response('hello')

        def _setup_view(app):
            app.add_url('/', '', view=_a_view)

        self.app = make_app(_setup_view, 'test_output')
        self.client = Client(self.app)

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
        app.connect_event('request-end', _process_request)
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
        app.connect_event('response-start', _process_response)
        app.add_url('/', '', view=_a_view)

    app = make_app(_setup_proc, 'test_output')
    c = Client(app)

    appiter, status, headers = c.open()

    assert list(appiter)[0] == 'byebye'

def test_local_processor():

    def _a_view(req):
        return Response('%s' % (local.foo == 1))

    def _local_proc(req):
        local.foo = 1

    def _setup_local(app):
        app.connect_event('request-start', _local_proc)
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
    assert h.meta() == '<meta />'

import glashammer.bundles.htmlhelpers as h

def test_generate_tag():
    assert h._generate_tag('br') == '<br />'

def test_binary():
    assert h._generate_tag('br', attr={'class':h._binary}) == '<br class />'

def test_h_meta():
    assert h.meta() == '<meta />'
    assert h.meta(name='banana') == '<meta name="banana" />'

def test_h_input():
    assert h.input_field('banana') == '<input type="text" name="banana" value="" id="banana" />'

def test_h_div():
    assert h._generate_tag('div', contents='Hello World') == '<div>Hello World</div>'

def test_h_textarea():
    assert h.textarea('a', 'hi') == '<textarea id="a" rows="10" cols="50" name="a">hi</textarea>'

def test_h_checkbox():
    assert h.checkbox('a') == '<input type="checkbox" name="a" value="yes" id="a" />'
    assert h.checkbox('a', checked=True) == ('<input checked type="checkbox" '
                                            'name="a" value="yes" id="a" />')

def test_h_radio():
    assert h.radio_button('a') == '<input type="radio" name="a" value="yes" id="a" />'
    assert h.radio_button('a', checked=True) == ('<input checked type="radio" '
                                            'name="a" value="yes" id="a" />')

def test_h_script():
    assert h.script('a') == '<script src="a" type="text/javascript"></script>'

def test_h_link():
    assert h.link('a', 'b') == '<link href="b" rel="a" />'

def test_h_jinjaallowed():
    assert h.jinja_allowed_attributes == ['input_field', 'checkbox',
                                          'radio_button', 'textarea']
    assert h.__all__ == ['input_field', 'checkbox',
                                          'radio_button', 'textarea']

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

# event map

def test_event_map():
    
    app = make_app(lambda app: None, 'test_output')

    from glashammer.utils.system import build_eventmap

    em = build_eventmap(app)

    assert 'app-setup' in em
    assert 'request-start' in em
    assert 'request-end' in em
    assert 'response-start' in em
    assert 'response-end' in em

# crypto

def test_pw_hash():
    assert check_pwhash(gen_pwhash('hello'), 'hello')

def test_unicode_pw_hash():
    assert check_pwhash(gen_pwhash(u'hello'), 'hello')
    assert check_pwhash(gen_pwhash('hello'), u'hello')

def test_bad_pw():
    assert not check_pwhash(gen_pwhash('hello'), 'byebye')

# i18n

def test_languages():
    """Might not work on your system"""
    app = make_app(i18n.setup_i18n, 'test_output')
    assert ('en', u'English') in i18n.list_languages()

def test_datetime():
    """Might not work on your system"""
    app = make_app(i18n.setup_i18n, 'test_output')
    dt = datetime(2008, 1, 2)
    assert i18n.format_datetime(dt) == 'Jan 2, 2008 12:00:00 AM'
    assert i18n.format_datetime(dt, 'short') == '1/2/08 12:00 AM'
    assert i18n.format_datetime(dt, 'long') == 'January 2, 2008 12:00:00 AM +0000'

def test_date():
    app = make_app(i18n.setup_i18n, 'test_output')
    d = date(2008, 1, 2)
    assert i18n.format_date(d) == 'Jan 2, 2008'
    assert i18n.format_date(d, 'short') == '1/2/08'
    assert i18n.format_date(d, 'long') == 'January 2, 2008'

def test_month():
    app = make_app(i18n.setup_i18n, 'test_output')
    d = date(2008, 1, 2)
    assert i18n.format_month(d) == 'January 08'

def test_time():
    app = make_app(i18n.setup_i18n, 'test_output')
    t = time()
    assert i18n.format_time(t) == '12:00:00 AM'
    assert i18n.format_time(t, 'short') == '12:00 AM'
    assert i18n.format_time(t, 'long') == '12:00:00 AM +0000'

# config

from glashammer.utils.config import unquote_value, quote_value, from_string, \
    get_converter_name

class TestConfig(object):

    def setup(self):
        try:
            os.unlink('test_output/config.ini')
        except OSError:
            pass
        self.conf = Configuration('test_output/config.ini')

    def test_read(self):
        f = open('test_output/config.ini', 'w')
        f.write('[main]\n')
        f.write('a = b\n')
        f.write('123\n')
        f.close()
        conf = Configuration('test_output/config.ini')

    def test_unquote_none(self):
        assert unquote_value(None) == ''
        assert unquote_value(0) == ''
        assert unquote_value(False) == ''

    def test_unquote_quoted(self):
        assert unquote_value("'a'") == 'a'
        assert unquote_value('"a"') == 'a'
        assert unquote_value('"a\'') == '"a\''

    def test_quote_none(self):
        assert quote_value(None) == ''
        assert quote_value(0) == ''
        assert quote_value(False) == ''

    def test_quote_word(self):
        assert quote_value('hello') == 'hello'

    def test_quote_complex(self):
        assert quote_value('"hello"') == '"\\"hello\\""'
        assert quote_value('hello\t') == '"hello\\t"'
        assert quote_value('hello\nhello') == '"hello\\nhello"'

    def test_from_string(self):
        assert from_string('True', bool, True)
        assert not from_string('true', bool, True)

    def test_bad_from_string(self):
        assert from_string('a', int, 'crazy_default') == 'crazy_default'

    def test_converter_name(self):
        assert get_converter_name(bool) == 'boolean'
        assert get_converter_name(int) == 'integer'
        assert get_converter_name(float) == 'float'
        assert get_converter_name(str) == 'string'
        assert get_converter_name('banana') == 'string'

    def test_not_write(self):
        assert not os.path.exists('test_output/config.ini')

    def test_add(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert self.conf['voo'] == 'noo'

    def test_change(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert self.conf['voo'] == 'noo'
        self.conf.change_single('voo', 'goo')
        assert os.path.exists('test_output/config.ini')
        assert self.conf['voo'] == 'goo'

        self.conf2 = Configuration('test_output/config.ini')
        self.conf2.config_vars['voo'] = (str, 'noo')
        assert self.conf2['voo'] == 'goo'

    def test_change_error(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert self.conf['voo'] == 'noo'
        assert self.conf.change_single('voo', 'goo')
        # change the mode of the file so we can't write to it
        os.chmod('test_output/config.ini', 0)
        assert not self.conf.change_single('voo', 'roo')

    def test_touch(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert self.conf['voo'] == 'noo'
        assert self.conf.change_single('voo', 'goo')
        self.conf.touch()

    def test_save(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert self.conf['voo'] == 'noo'
        self.conf.change_single('voo', 'goo')
        assert self.conf['voo'] == 'goo'

    def test_change_external(self):
        assert not self.conf.changed_external
        self.conf.config_vars['voo'] = (str, 'noo')
        assert self.conf['voo'] == 'noo'
        self.conf.change_single('voo', 'goo')
        assert self.conf['voo'] == 'goo'
        assert self.conf.changed_external

        f = open('test_output/config.ini', 'a')
        f.write('\n\n\n')
        f.close()

        assert self.conf.changed_external

    def test_iter(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert list(self.conf) == ['voo']

    def test_contains(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert 'voo' in self.conf
        assert 'noo' not in self.conf

    def test_itervalues(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert list(self.conf.itervalues()) == ['noo']

    def test_iteritems(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert list(self.conf.iteritems()) == [('voo', 'noo')]

    def test_repr(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        assert repr(self.conf) == "<Configuration {'voo': 'noo'}>"

    def test_trans_revert(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        self.conf.change_single('voo', 'goo')
        assert self.conf['voo'] == 'goo'
        t = self.conf.edit()
        t.revert_to_default('voo')
        assert t['voo'] == 'noo'
        t.commit()
        assert self.conf['voo'] == 'noo'

    def test_trans_keyerror(self):
        def bad_get():
            return self.conf.edit()['hoo']
        assert_raises(KeyError, bad_get)

    def test_trans_converted_values(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        t = self.conf.edit()
        t['voo'] = 'woo'
        assert t['voo'] == 'woo'
        assert self.conf['voo'] == 'noo'
        t.commit()
        assert self.conf['voo'] == 'woo'

    def test_set_from_string(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        t = self.conf.edit()
        t.set_from_string('voo', 'ioo', True)
        t.commit()
        assert self.conf['voo'] == 'ioo'

    def test_trans_update(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        t = self.conf.edit()
        t.update([('voo', 'hoo')])
        t.commit()
        assert self.conf['voo'] == 'hoo'

    def test_uncommitted_commit(self):
        self.conf.config_vars['voo'] = (str, 'noo')
        t = self.conf.edit()
        t.commit()
        assert self.conf['voo'] == 'noo'





from glashammer.utils.log import debug, info, warning, error

def test_debug():
    debug('testing debug')

def test_info():
    info('testing info')

def test_warning():
    warning('testing warning')

def test_errror():
    error('testing error')

def test_event_log_handler():
    
    logs = []

    def log(level, record):
        logs.append((level, record))

    def setup_app(app):
        app.connect_event('log', log)

    app = make_app(setup_app, 'test_output')
    c = Client(app)
    c.open()
    assert len(logs) > 5

# Auth
def test_check_username_password():
    from glashammer.bundles.auth import setup_auth, check_username_password

    called = []

    def check(u, p):
        called.append((u, p))
        return u == p

    def view(req):
        assert check_username_password('a', 'a')
        assert not check_username_password('a', 'b')
        return Response()

    def setup_app(app):
        app.add_setup(setup_auth)
        app.connect_event('password-check', check)
        app.add_url('/', 'a/b', view=view)

    app = make_app(setup_app, 'test_output')
    c = Client(app)
    c.open()


def test_check_login():
    from glashammer.bundles.auth import setup_auth, login
    from glashammer.bundles.sessions import get_session

    called = []

    def check(u, p):
        called.append((u, p))
        return u == p

    def view(req):
        login('a')
        return Response()

    def setup_app(app):
        app.add_setup(setup_auth)
        app.connect_event('password-check', check)
        app.add_url('/', 'a/b', view=view)

    app = make_app(setup_app, 'test_output')
    c = Client(app)
    c.open()

    session = get_session()
    token_key = get_app().conf['auth/token_key']
    assert token_key in session
    assert session[token_key] == 'a'


def test_check_role():
    from glashammer.bundles.auth import setup_auth, check_role
    from glashammer.bundles.sessions import get_session

    called = []

    def check(u, p):
        called.append((u, p))
        return u == p

    def view(req):
        assert check_role('a', 'a')
        assert not check_role('c', 'd')
        return Response()

    def setup_app(app):
        app.add_setup(setup_auth)
        app.connect_event('role-check', check)
        app.add_url('/', 'a/b', view=view)

    app = make_app(setup_app, 'test_output')
    c = Client(app)
    c.open()

# Pagination Helper

from glashammer.utils.webbish import Pagination

class TestPagination(object):

    def setup(self):

        def view(req):
            return Response(self.p.generate(next_link=True, prev_link=True))

        def setup_app(app):
            app.add_url('/', 'app/page', view=view)

        app = make_app(setup_app, 'test_output')
        self.c = Client(app)
        self.p = Pagination('app/page', 3, 10, 500)

    def test_generate(self):
        iter, status, heaaders = self.c.open()
        s = ''.join(iter)
        assert s == """
<a href="/?page=2">&laquo; Prev</a> <a href="/?page=1">1</a><span class="commata">,
</span><a href="/?page=2">2</a><span class="commata">,
</span><strong>3</strong><span class="commata">,
</span><a href="/?page=4">4</a><span class="commata">,
</span><a href="/?page=5">5</a><span class="ellipsis">...
</span><a href="/?page=49">49</a><span class="commata">,
</span><a href="/?page=50">50</a> <a href="/?page=4">Next &raquo;</a>
""".strip()




# openid

def test_openid():

    def setup_openid(app):
        from glashammer.bundles.openidauth import setup_openid
        app.add_setup(setup_openid)

    app = make_app(setup_openid, 'test_output')

    c = Client(app)
    iter, status, headers = c.post('/openid/login',
        data={'openid':'http://unpythonic.blogspot.com'})

    assert '302' in status


# http redirects

def _boo_view(req):
    return redirect('/home')

def _foo_view(req):
    return redirect_to('test/home')

def _home_view(req):
    return Response('hello')

def _setup_redirect_app(app):
    app.add_url('/home', 'test/home', _home_view)
    app.add_url('/foo', 'test/foo', _foo_view)
    app.add_url('/boo', 'test/boo', _boo_view)



def _test_redirect_helper(getpath):
    app = make_app(_setup_redirect_app, 'test_output')

    c = Client(app)
    appiter, status, headers = c.open('/foo')

    s = list(appiter)[0]

    location = dict(headers).get('Location')

    assert location

    path = urlparse.urlparse(location)[2]

    assert path == '/home'

def test_redirect():
    _test_redirect_helper('/foo')

def test_redirect_to():
    _test_redirect_helper('/boo')



# functional tests for examples

from glashammer.utils.system import load_app_from_path

class TestHelloWorld(object):

    def setup(self):
        app = load_app_from_path('examples/helloworld/run.py')
        self.c = Client(app)

    def test_index(self):
        iter, status, headers = self.c.open()
        assert ' '.join(iter) == '<h1>Hello World</h1>'
        assert status == '200 OK'

    def test_notfound(self):
        iter, status, headers = self.c.open('/blah')
        assert status == '404 NOT FOUND'
        assert '404 Not Found' in ' '.join(iter)


class TestNotes(object):

    def setup(self):
        app = load_app_from_path('examples/notes/notes.py')
        self.c = Client(app)

    def test_index(self):
        iter, status, headers = self.c.open()
        assert 'form action="/add" method="post"' in ''.join(iter)

from simplejson import loads

class TestJsonRest(object):

    def setup(self):
        app = load_app_from_path('examples/jsonrest/run.py')
        self.c = Client(app)

    def test_index(self):
        iter, status, headers = self.c.open()
        s = ''.join(iter)
        assert  """
    <a href="#" id="get_link">GET</a>
    <a href="#" id="post_link">POST</a>
    <a href="#" id="put_link">PUT</a>
    <a href="#" id="delete_link">DELETE</a>
""".strip('\n') in s

    def test_get(self):
        iter, status, headers = self.c.open('/svc')
        d = loads(''.join(iter))
        assert d['type'] == 'GET'

    def test_put(self):
        iter, status, headers = self.c.put('/svc')
        d = loads(''.join(iter))
        assert d['type'] == 'PUT'

    def test_delete(self):
        iter, status, headers = self.c.delete('/svc')
        d = loads(''.join(iter))
        assert d['type'] == 'DELETE'

    def test_post(self):
        iter, status, headers = self.c.post('/svc')
        d = loads(''.join(iter))
        assert d['type'] == 'POST'



