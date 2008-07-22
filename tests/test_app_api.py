
import os

from glashammer.application import GlashammerApplication

def make_app(setup_func, instance_dir=None):
    return GlashammerApplication(setup_func, instance_dir)



# Basics

def _setup_empty(app):
    return

def test_make_app():
    app = make_app(_setup_empty, 'test_output')

def test_app_no_instance():
    """
    Test creating an application with no instance directory (BROKEN)
    """
    app = make_app(_setup_empty)


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

def test_add_view():
    """
    Adding a rule, endpoint and view, and that it's called.
    """
    def _add_view_setup(app):
        app.add_url('/', endpoint='foo/blah', view=_aview)
    app = make_app(_add_view_setup, 'test_output')
    assert _has_rule(app.map, '/', 'foo/blah')
    assert app.get_view(None, 'foo/blah', {}) == 1


