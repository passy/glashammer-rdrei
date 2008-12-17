# -*- coding: utf-8 -*-
"""
    glashammer.utils.http
    ~~~~~~~~~~~~~~~~~~~~~

    from zine.utils.http

    Various HTTP related helpers.

    :copyright: 2008 by Armin Ronacher.
    (with minor changes by Ali Afshar)
    :license: MIT/BSD
"""
from urlparse import urlparse, urljoin

from werkzeug import redirect as _redirect
from werkzeug.exceptions import BadRequest

from glashammer.utils.local import get_app, get_request, url_for

# zine compat
get_application = get_app

def check_external_url(*args):
    pass


def get_redirect_target(invalid_targets=(), request=None):
    """Check the request and get the redirect target if possible.
    If not this function returns just `None`.
    """
    if request is None:
        request = get_request()
    check_target = request.values.get('_redirect_target') or \
                   request.args.get('next') or \
                   request.environ.get('HTTP_REFERER')

    print check_target

    # if there is no information in either the form data
    # or the wsgi environment about a jump target we have
    # to use the target url
    if not check_target:
        return


    return check_target


def redirect(url, code=302, allow_external_redirect=False):
    """Return a redirect response.  Like Werkzeug's redirect.
    """
    if allow_external_redirect:
        import warnings
        warnings.warn('allow_external_redirect argument is depracated',
            category=DeprecationWarning)
    return _redirect(url, code)


def redirect_to(*args, **kwargs):
    """Temporarily redirect to an URL rule."""
    return redirect(url_for(*args, **kwargs))


def redirect_back(*args, **kwargs):
    """Redirect back to the page we are comming from or the URL
    rule given.
    """
    target = get_redirect_target()
    if target is None:
        target = url_for(*args, **kwargs)
    return redirect(target)
