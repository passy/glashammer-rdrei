
from glashammer.utils import Response
from glashammer.utils.appliance import Appliance, expose

from werkzeug.test import Client
from tests import gh_app


class Pages(Appliance):

    @expose('/')
    def index(self, req):
        return Response('hello')

def _setup(app):
    p = Pages(mountpoint_path='/pages')
    app.add_setup(p)

def test_appliance():
    gh_app(_setup)

def test_autorules():
    p = Pages()
    urls = list(p._find_rules())
    print dir(urls[0])
    assert urls[0].rule == '/'

def test_autorules_client():
    app = gh_app(_setup)
    c = Client(app)

    i, s, h = c.open('/')
    assert '404' in s

    i, s, h = c.open('/pages/')
    print i, s, h
    assert '200' in s
    assert 'hello' in ''.join(i)
