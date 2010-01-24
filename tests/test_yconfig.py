

import os, tempfile

from glashammer.application import declare_app
from werkzeug.test import Client

def _c(y):
    fd, fn = tempfile.mkstemp(suffix='_gh-yconfig-test')
    os.write(fd, y)
    os.close(fd)
    return fn

def test_empty():
    app = declare_app(_c(''))
    assert app

def test_urls():
    yaml = """
urls:
    - url: /foo
      endpoint: foo
      view: os.path
""".strip()

    fn = _c(yaml)

    app = declare_app(fn)
    assert app
    assert 'foo' in app.map._rules_by_endpoint
    assert app.map._rules_by_endpoint['foo'][0].rule == '/foo'


def test_settings():
    yaml = """
settings:
    a: 1
    b: banana
    c:
        - embedded
        - list
""".strip()

    fn = _c(yaml)
    app = declare_app(fn)

def test_template_searchpaths():
    yaml = """
template_searchpaths:
    - /foo
    - /blah
""".strip()

    fn = _c(yaml)
    app = declare_app(fn)

    assert '/foo' in app.template_env.loader.searchpath
    assert '/blah' in app.template_env.loader.searchpath


def test_shared():
    yaml = """
shared:
    - name: foo
      path: /blah
    - name: moo
      path: /gah
""".strip()

    fn = _c(yaml)
    app = declare_app(fn)

    print app.shared_export_map

    assert '/_shared/foo' in app.shared_export_map
    assert app.shared_export_map['/_shared/foo'] == '/blah'

    assert '/_shared/moo' in app.shared_export_map
    assert app.shared_export_map['/_shared/moo'] == '/gah'


def test_appliance():
    yaml = """
appliances:
    - import: glashammer.utils.appliance._JustForTestingAppliance
      mountpoint_path: /pages
    """.strip()
    fn = _c(yaml)
    app = declare_app(fn)

    c = Client(app)

    i, s, h = c.open('/')
    assert '404' in s

    i, s, h = c.open('/pages/')
    print i, s, h
    assert '200' in s
    assert 'hello' in ''.join(i)


def test_instance_dir():
    yaml = ''
    fn = _c(yaml)
    app = declare_app(fn)
    assert  app.instance_dir == '/tmp/instance'



