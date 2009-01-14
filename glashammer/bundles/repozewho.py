
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
import os, sys
log_stream = sys.stdout

dict(
            identifiers,
            authenticators,
            challengers,
            mdproviders,
            default_request_classifier,
            default_challenge_decider,
            log_stream = log_stream,
            log_level = logging.DEBUG
)

import logging
def middleware_factory(app, configfile=None, **kw):
    if configfile is not None:
        from repoze.who.config import make_middleware_with_config
        middleware = make_middleware_with_config(app, '/path/to/who.ini')
    elif kw:
        middleware = PluggableAuthenticationMiddleware(
            app,
            identifiers,
            authenticators,
            challengers,
            mdproviders,
            default_request_classifier,
            default_challenge_decider,
            log_stream = log_stream,
            log_level = logging.DEBUG
        )
    else:
        raise ValueError('Must either provide a configuration file, or kw')
    return middleware


def setup_repozewho(app, configfile=None, **kw):
    
    app.add_middleware(middleware_factory)


