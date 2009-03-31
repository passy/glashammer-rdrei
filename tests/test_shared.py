
from werkzeug.test import Client

from glashammer import make_app
from glashammer.utils import url_for, Response

def _view(req):
    s = url_for('shared/test', filename='blah')
    return Response(s)


def _setup(app):
    app.add_shared('test', 'tests')
    app.add_shared('', 'tests')
    app.add_url('/', 'test/main', _view)


def test_url():
    app = make_app(_setup, 'test_output')
    c = Client(app)
    appiter, code, headers = c.open('/')
    assert ''.join(appiter) == '/_shared/test/blah'


def test_shared_file():
    app = make_app(_setup, 'test_output')
    c = Client(app)
    appiter, code, headers = c.open('/_shared/test/test_shared.py')
    assert 'add_shared' in ''.join(appiter)
    assert dict(headers)['Content-Type'] == 'text/x-python'

def test_shared_dir():
    app = make_app(_setup, 'test_output')
    c = Client(app)
    appiter, code, headers = c.open('/_shared/test/')
    assert '404 NOT FOUND' == code

def test_empty_name():
    app = make_app(_setup, 'test_output')
    c = Client(app)
    appiter, code, headers = c.open('/_shared/test_shared.py')
    assert 'add_shared' in ''.join(appiter)
    assert dict(headers)['Content-Type'] == 'text/x-python'

