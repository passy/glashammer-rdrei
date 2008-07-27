
import os

from glashammer import run_very_simple, make_app, Response

from glashammer.bundles.auth import setup_auth, auth_protected_view

def setup(app):
    app.add_setup(setup_auth)
    app.connect_event('password-check', dumb_password_checker)
    app.add_url('/', 'home', view=homepage_view)

def dumb_password_checker(username, password):
    return True

@auth_protected_view
def homepage_view(req):
    return Response(
        '<h1>Hello, authorized world!</h1>'
        '<a href="/logout">Log Out</a>'
    )

if __name__ == '__main__':
    app = make_app(setup, os.path.dirname(__file__))
    run_very_simple(app)



