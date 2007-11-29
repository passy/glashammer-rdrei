

"""
Really simple auth.
"""

import os

from glashammer.controller import Controller
from glashammer.service import Service
from glashammer.utils import Response, RedirectResponse, Request
from glashammer.stormintegration import StormBase, Unicode

from werkzeug.routing import RequestRedirect, Rule

class NotAuthenticatedError(Exception):
    pass

class NotAuthorizedError(Exception):
    pass

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'auth_templates')


class AuthController(Controller):

    def login(self, req):
        if req.method == 'POST':
            redirect = req.form.get('login_redirect_back_to', '/')
            username = req.form.get('username')
            password = req.form.get('password')
            if not (username and password):
                return self._login_failure(redirect)
            user = self.site.store.find(User, username=username,
                                        password=password).any()
            if user is None:
                return self._login_failure(redirect)
            else:
                self.session['user_id'] = username
                return RedirectResponse(redirect)
        else:
            redirect_back_to = req.args.get('attempted_page', '')
            return self.create_template_response('loginform.jinja',
                redirect_back_to = redirect_back_to,
            )

    def _login_failure(self, redirect):
        return RedirectResponse(self.map_adapter.build('auth/login',
                                dict(attempted_page=redirect)))


    def logout(self, req):
        redirect = req.args.get('logout_redirect_back_to', '/')
        self.session['user_id'] = 0
        return RedirectResponse(redirect)


class AuthMiddleware(object):

    def __init__(self, app, site):
        self.app = app
        self.site = site

    def __call__(self, environ, start_response):
        session = environ['werkzeug.session']
        environ['glashammer.user_id'] = session.get('user_id')
        try:
            return self.app(environ, start_response)
        except NotAuthenticatedError:
            map_adapter = self.site.url_map.bind_to_environ(environ)
            req = Request(environ, map_adapter)
            resp = RedirectResponse(
                map_adapter.build('auth/login',
                    dict(attempted_page=req.url))
                )
            return resp(environ, start_response)
        except NotAuthorizedError:
            return Response('Forbidden', status=403)(environ, start_response)
        

class Permission(object):

    def __call__(self, user_id):
        raise NotImplementedError


class PublicPermission(object):

    def __call__(self, site, user_id):
        return True


class UserPermission(Permission):

    def __init__(self, site, user_id):
        if not user_id:
            raise NotAuthenticatedError


class AdminPermission(UserPermission):

    def __call__(self, site, user_id):
        UserPermission.__call__(self, site, user_id)
        if user_id == 'hoo':
            return True
        else:
            raise NotAuthorizedError





class User(StormBase):

    __storm_table__ = 'user'

    username = Unicode()
    password = Unicode()


class AuthService(Service):

    def lifecycle(self):
        self.register_controller('auth', AuthController)
        self.register_url_rules(
            Rule('/login', endpoint='auth/login'),
            Rule('/logout', endpoint='auth/logout'),
        )
        self.register_template_directory(TEMPLATE_PATH)

    def finalise(self):
        store = self.store
        try:
            User.create_table(store)
        except:
            pass
        if store.find(User).any() is None:
            u = User()
            u.username = u'ali'
            u.password = u'ali'
            store.add(u)
        store.flush()
        store.commit()

    def create_middleware(self, app):
        return AuthMiddleware(app, self.site)
