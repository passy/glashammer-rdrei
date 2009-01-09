
from unittest import TestCase

from glashammer import make_app, Response

from werkzeug.test import Client

def _authd_view(req):
    if not req.environ.get('repoze.who.identity'):
        return Response(status=401)
    else:
        return Response('ok')


def _setup(app):
    from glashammer.bundles.repozewho import setup_repozewho
    app.add_setup(setup_repozewho)
    app.add_url('/', 'home', _authd_view)


class TestRepozeWho(TestCase):

    def setUp(self):
        self.app = make_app(_setup)
        self.c = Client(self.app)

    def get(self, url='/'):
        appiter, status, headers = self.c.open(url)
        return ''.join(appiter)

    def post(self, login, password, do_login=True, url='/'):
        if do_login:
            url = url + '?__do_login=true'
        appiter, status, headers = self.c.post(url,
            data=dict(login=login, password=password))
        return appiter, status, headers

    def test_starts(self):
        assert '<form' in self.get()

    def test_good_login(self):
        appiter, status, headers = self.post('admin', 'admin')
        assert status.startswith('302')
        assert self.get() == 'ok'

    def test_bad_login(self):
        appiter, status, headers = self.post('a', 'a')
        assert status.startswith('302')
        assert self.get() != 'ok'

    def test_nocookie_client(self):
        self.c = Client(self.app, use_cookies=False)
        appiter, status, headers = self.post('admin', 'admin')
        assert status.startswith('302')
        assert self.get() != 'ok'

