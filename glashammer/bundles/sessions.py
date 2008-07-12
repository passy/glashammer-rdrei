

from werkzeug.contrib.securecookie import SecureCookie
from glashammer.utils import local, get_app

def get_session():
    return local.session

def setup_session(request):
    app = get_app()
    cookie_name = app.conf['sessionse/cookie_name']
    session = SecureCookie.load_cookie(self, cookie_name,
                                           app.conf['secret_key'])
    local.session = session

def cleanup_sessions(response):
    # save the session
    if request.session.should_save:
        cookie_name = self.conf['session_cookie_name']
        if request.session.get('pmt'):
            max_age = 60 * 60 * 24 * 31
            expires = time() + max_age
        else:
            max_age = expires = None
        request.session.save_cookie(response, cookie_name, max_age=max_age,
                                    expires=expires, session_expires=expires)

def setup_sessions(app):
    app.add_config_var('sessions/cookie_name', 'glashammer_session', str)
    app.add_config_var('sessions/secret', 'glashammer_secret', str)

    app.add_request_processor(setup_session)
    app.add_response_processor(cleanup_sessions)

