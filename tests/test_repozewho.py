
from unittest import TestCase

from glashammer import make_app
from glashammer.utils import Response

from werkzeug.test import Client


from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.cookie import InsecureCookiePlugin
from repoze.who.plugins.form import FormPlugin
from repoze.who.plugins.htpasswd import HTPasswdPlugin

from StringIO import StringIO
io = StringIO()
salt = 'aa'
for name, password in [ ('admin', 'admin'), ('chris', 'chris') ]:
    io.write('%s:%s\n' % (name, password))
io.seek(0)
def cleartext_check(password, hashed):
    return password == hashed
htpasswd = HTPasswdPlugin(io, cleartext_check)
basicauth = BasicAuthPlugin('repoze.who')
auth_tkt = AuthTktCookiePlugin('secret', 'auth_tkt')
form = FormPlugin('__do_login', rememberer_name='auth_tkt')
form.classifications = { IIdentifier:['browser'],
                         IChallenger:['browser'] } # only for browser
identifiers = [('form', form),('auth_tkt',auth_tkt),('basicauth',basicauth)]
authenticators = [('htpasswd', htpasswd)]
challengers = [('form',form), ('basicauth',basicauth)]
mdproviders = []

from repoze.who.classifiers import default_request_classifier
from repoze.who.classifiers import default_challenge_decider
log_stream = None
import logging
import os, sys
log_stream = sys.stdout


kw=dict(
    identifiers=identifiers,
    authenticators=authenticators,
    challengers=challengers,
    mdproviders=mdproviders,
    classifier=default_request_classifier,
    challenge_decider=default_challenge_decider,
)


def _authd_view(req):
    if not req.environ.get('repoze.who.identity'):
        return Response(status=401)
    else:
        return Response('ok')

def _setup(app):
    from glashammer.bundles.repozewho import setup_repozewho
    app.add_setup(setup_repozewho, **kw)
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

