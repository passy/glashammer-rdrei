
"""
Open ID Support for Glashammer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from openid.consumer.consumer import Consumer

from werkzeug import redirect

from glashammer.utils import sibpath, url_for

from glashammer.bundles.sessions import setup_sessions, get_session

def login_view2(req):
    pass

def login_view(req):
    url = req.form.get('openid')
    consumer = Consumer(get_session(), None)
    authreq = consumer.begin(url)
    url_back = url_for('openid/login2', _external=True)
    return redirect(authreq.redirectURL(url_back, url_back))

def setup_openid(app):
    app.add_setup(setup_sessions)

    app.add_url('/openid/login', endpoint='openid/login', view=login_view)
    app.add_url('/openid/login2', endpoint='openid/login2', view=login_view2)
