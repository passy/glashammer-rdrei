# -*- coding: utf-8 -*-
"""
    glashammer.bundles.forms
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2008 by Glashammer Developers
    :license: MIT
"""

from wtforms import HiddenField

from glashammer.utils import sibpath

class IdField(HiddenField):
    def _value(self):
	    return self.data and unicode(self.data) or u'0'

    def process_formdata(self, valuelist):
        try:
            self.data = int(valuelist[0])
            if self.data == 0:
                self.data = None
        except ValueError:
            self.data = None


def make_hidden_fields(*fields):
    """Create some hidden form data for fields."""
    buf = []
    for field in fields:
        args = field.get_hidden_field()
        if args is not None:
            buf.append(u'<input type="hidden" name="%s" value="%s">' %
                       (escape(args[0]), escape(args[1])))
    return u'\n'.join(buf)

class HiddenFormField(object):
    """Baseclass for special hidden fields."""

    def get_hidden_field(self):
        pass

    def __unicode__(self):
        return make_hidden_fields(self)

class CSRFProtector(HiddenFormField):
    """This class is used in the admin panel to avoid CSRF attacks.

    In the controller code just create a new instance of the CSRFProtector
    and pass it the request object.  The instance then provides a method
    called `assert_safe` that must be called before the action takes place.

    Example::

        protector = CSRFProtector()
        if request.method == 'POST':
            protector.assert_safe()
            ...

        return render_response(..., hidden_data=make_hidden_fields(protector))

    Additionally you have to add some small code to the templates.  If you
    want to protect POST requests it's enough to do ``{{ protector }}``
    (assuming protector is the CSRFProtector object from the controller
    function) or ``<a href="...?{{ protector.url_value|e }}">`` if you want
    to protect a GET request.

    If you don't want or have to combine it with other hidden fields
    such as the intelligent redirect stuff you can also pass the protector
    instance to the template directly, rendering it prints out the hidden
    field automatically. This also allows you to access the `url_value`
    attribute that allows CSRF protection for GET requests.
    """

    def __init__(self):
        self.request = request = local.request
        self.token = sha.new('%s|%s|%s|%s' % (
            request.path,
            local.application.conf['secret_key'],
            request.user.user_id,
            request.user.is_somebody
        )).hexdigest()

    @property
    def url_value(self):
        return '_csrf_check_token=%s' % url_quote(self.token)

    def assert_safe(self):
        if self.request.values.get('_csrf_check_token') != self.token:
            raise Forbidden()

    def get_hidden_field(self):
        return '_csrf_check_token', self.token

class IntelligentRedirect(HiddenFormField):
    """An intelligent redirect tries to go back to the page the user
    is comming from or redirects to the url rule provided when called.

    Like the `CSRFProtector` it uses hidden form information.

    Example usage::

        redirect = IntelligentRedirect()
        if request.method == 'POST':
            ...
            return redirect('admin/index') # go back to the admin index or the
                                           # page we're comming from.
        return render_response(..., hidden_data=make_hidden_fields(redirect))

    If you don't want to combine it with other hidden fields you can ignore
    the `make_hidden_fields` call and pass the intelligent redirect instance
    directly to the template.  Rendering it results in a hidden form field.

    The intelligent redirect is much slower than a normal redirect because
    it tests for quite a few things. Don't use it if you don't have to.
    """

    def __init__(self):
        self.request = local.request
        self.invalid_targets = []

    def add_invalid(self, *args, **kwargs):
        """Add an invalid target. Invalid targets are URLs we don't want to
        visit again. For example if a post is deleted from the post edit page
        it's a bad idea to redirect back to the edit page because in that
        situation the edit page would return a page not found.
        """
        from textpress.application import url_for
        self.invalid_targets.append(url_for(*args, **kwargs))

    def get_redirect_target(self):
        """Check the request and get the redirect target if possible.
        If not this function returns just `None`.
        """
        return None
        check_target = self.request.values.get('_redirect_target') or \
                       self.request.args.get('next') or \
                       self.request.environ.get('HTTP_REFERER')

        # if there is no information in either the form data
        # or the wsgi environment about a jump target we have
        # to use the target url
        if not check_target:
            return

        blog_url = self.request.app.cfg['blog_url']
        blog_parts = urlparse(blog_url)
        check_parts = urlparse(urljoin(blog_url, check_target))

        # if the jump target is on a different server we probably have
        # a security problem and better try to use the target url.
        if blog_parts[:2] != check_parts[:2]:
            return

        # if the jump url is the same url as the current url we've had
        # a bad redirect before and use the target url to not create a
        # infinite redirect.
        current_parts = urlparse(urljoin(blog_url, self.request.path))
        if check_parts[:5] == current_parts[:5]:
            return

        # if the `check_target` is one of the invalid targets we also
        # fall back.
        for invalid in self.invalid_targets:
            if check_parts[:5] == urlparse(urljoin(blog_url, invalid))[:5]:
                return

        return check_target

    def __call__(self, *args, **kwargs):
        """Trigger the redirect."""
        from glashammer.utils import redirect, url_for
        target = self.get_redirect_target()
        if target is None:
            target = url_for(*args, **kwargs)
        return redirect(target)

    def get_hidden_field(self):
        target = self.get_redirect_target()
        if target is None:
            return
        return '_redirect_target', target


def setup_forms(app):
    app.add_template_searchpath(sibpath(__file__, 'templates'))

setup_app = setup_forms


