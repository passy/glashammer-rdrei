
import os

from glashammer.application import GlashammerApplication

def make_app(setup_func, instance_dir=None):
    return GlashammerApplication(setup_func, instance_dir)


def _setup_empty(app):
    return

def _aview(req):
    return 1

def test_make_app():
    def my_empty_setup(app):
        return
    app = make_app(my_empty_setup, 'test_output')

def test_app_no_instance():
    def my_empty_setup(app):
        return
    app = make_app(my_empty_setup)

# View and endpoints

def _has_rule(map, url, endpoint):
    return (url, endpoint) in [(i.rule, i.endpoint) for i in map.iter_rules()]

def _add_rule_setup(app):
    app.add_url('/', endpoint='foo/blah')

def test_add_rule():
    app = make_app(_add_rule_setup, 'test_output')
    assert _has_rule(app.map, '/', 'foo/blah')

def _add_view_setup(app):
    app.add_url('/', endpoint='foo/blah', view=_aview)

def test_add_view():
    app = make_app(_add_view_setup, 'test_output')
    assert _has_rule(app.map, '/', 'foo/blah')
    assert app.get_view(None, 'foo/blah', {}) == 1


