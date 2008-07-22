
from werkzeug.contrib.securecookie import SecureCookie
from glashammer.utils import local, get_app, get_request

def get_session():
    return local.session

def setup_session(request):
    app = get_app()
    req = get_request()
    cookie_name = app.conf['sessions/cookie_name']
    session = SecureCookie.load_cookie(req, cookie_name,
                                           app.conf['sessions/secret'])
    local.session = session

def cleanup_sessions(response):
    # save the session
    app = get_app()
    session = get_session()
    if session.should_save:
        cookie_name = app.conf['sessions/cookie_name']
        if session.get('pmt'):
            max_age = 60 * 60 * 24 * 31
            expires = time() + max_age
        else:
            max_age = expires = None
        session.save_cookie(response, cookie_name, max_age=max_age,
                            expires=expires, session_expires=expires)

def setup_sessions(app):
    app.add_config_var('sessions/cookie_name', 'glashammer_session', str)
    app.add_config_var('sessions/secret', 'glashammer_secret', str)

    app.add_request_processor(setup_session)
    app.add_response_processor(cleanup_sessions)

setup_app = setup_sessions

