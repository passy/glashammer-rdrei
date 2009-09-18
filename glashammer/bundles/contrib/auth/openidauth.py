
"""
Open ID Support for Glashammer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from openid.consumer.consumer import Consumer, SUCCESS, CANCEL

from werkzeug import redirect

from glashammer.utils import sibpath, url_for, Response

from glashammer.bundles.sessions import setup_sessions, get_session
from glashammer.bundles.auth import setup_auth, login


def login_view(req):
    session = get_session()
    consumer = Consumer(session, None)
    url_back = url_for('openid/login', _external=True)
    if req.method == 'POST':
        url = req.form.get('openid')
        authreq = consumer.begin(url)
        return redirect(authreq.redirectURL(url_back, url_back))
    else:
        res = consumer.complete(req.args, url_back)
        if res.status == SUCCESS:
            identity = req.args.get('openid.identity')
            login(identity)
            return Response('Successfully logged in as: %s' % identity)
        elif res.status == CANCEL:
            return Response('Cancelled')
        else:
            return Response('Nope')
        print res == SUCCESS


def setup_openid(app):
    app.add_setup(setup_sessions)
    app.add_setup(setup_auth)

    app.add_url('/openid/login', 'openid/login', view=login_view)
