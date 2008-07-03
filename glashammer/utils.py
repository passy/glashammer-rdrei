
import os, string, sha, math, linecache, _ast
from collections import deque
from random import choice, randrange, random

import pytz

from simplejson import dumps as dump_json, loads as load_json

from werkzeug import run_simple, Request as wzRequest, \
    Response as wzResponse, ClosingIterator, Local, LocalManager, redirect, \
    escape
from werkzeug.contrib.securecookie import SecureCookie
from werkzeug.exceptions import Forbidden

local = Local()
local_manager = LocalManager([local])


SALT_CHARS = string.ascii_lowercase + string.digits

DATE_FORMATS = ['%m/%d/%Y', '%d/%m/%Y', '%Y%m%d', '%d. %m. %Y',
                '%m/%d/%y', '%d/%m/%y', '%d%m%y', '%m%d%y', '%y%m%d']
TIME_FORMATS = ['%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p']


def format_datetime(obj, format=None):
    """Format a datetime object. Later with i18n"""
    format = DATE_FORMATS[3]
    return obj.strftime(format)
    cfg = local.application.conf
    tzinfo = pytz.timezone(str(cfg['timezone']))
    if type(obj) is date:
        obj = datetime(obj.year, obj.month, obj.day, tzinfo=tzinfo)
    else:
        obj = obj.replace(tzinfo=tzinfo)
    if format is None:
        format = cfg['datetime_format']
    return obj.strftime(format.encode('utf-8')).decode('utf-8')

def render_template(template_name, _stream=False, **context):
    #emit_event('before-render-template', template_name, _stream, context)
    tmpl = local.application.template_env.get_template(template_name)
    if _stream:
        return tmpl.stream(context)
    return tmpl.render(context)

def render_response(template_name, mimetype='text/html', **context):
    """Render a template and return a response instance.

    `template_name` The name of the template to use, this can include a relative
    path to the template from the searchpath directory.

    `mimetype` The mimetype for the response.

    `context` Key worded context variables for the template. These variables are
    passed into the template namespace.
    """
    return Response(
        render_template(template_name, **context),
        mimetype=mimetype
    )

def url_for(endpoint, **args):
    """Get the url to an endpoint."""
    if hasattr(endpoint, 'get_url_values'):
        rv = endpoint.get_url_values()
        if rv is not None:
            endpoint, updated_args = rv
            args.update(updated_args)
    anchor = args.pop('_anchor', None)
    external = args.pop('_external', False)
    rv = local.url_adapter.build(endpoint, args,
                                 force_external=external)
    if anchor is not None:
        rv += '#' + url_quote(anchor)
    return rv

def get_request():
    return local.request

class Response(wzResponse):
    default_mimetype = 'text/html'

class JSonResponse(wzResponse):
    default_mimetype = 'text/javascript'

    def __init__(self, data, *args, **kw):
        wzResponse.__init__(self, dump_json(data), *args, **kw)

class Request(wzRequest):
    """The used request class."""

    def __init__(self, app, environ):
        wzRequest.__init__(self, environ)
        self.app = app

        engine = self.app.db_engine

        # get the session and try to get the user object for this request.
        from glashammer.bundles.auth.database import User
        user = None
        cookie_name = app.conf['session_cookie_name']
        session = SecureCookie.load_cookie(self, cookie_name,
                                           app.conf['secret_key'])
        user_id = session.get('uid')
        if user_id:
            user = User.objects.get(user_id)
        if user is None:
            user = User.objects.get_nobody()
        self.user = user
        self.session = session


    def login(self, user, permanent=False):
        """Log the given user in. Can be user_id, username or
        a full blown user object.
        """
        from glashammer.bundles.auth.database import User
        if isinstance(user, (int, long)):
            user = User.objects.get(user)
        elif isinstance(user, basestring):
            user = User.objects.filter_by(username=user).first()
        if user is None:
            raise RuntimeError('User does not exist')
        print user
        self.user = user
        #! called after a user was logged in successfully
        emit_event('after-user-login', user)
        self.session['uid'] = user.user_id
        print self.session
        print self.session['uid']
        if permanent:
            self.session['pmt'] = True

    def logout(self):
        """Log the current user out."""
        from glashammer.bundles.auth.database import User
        user = self.user
        self.user = User.objects.get_nobody()
        self.session.clear()
        #! called after a user was logged out and the session cleared.
        emit_event('after-user-logout', user)


def get_app():
    return local.application

def run_very_simple(app):
    from werkzeug.debug import DebuggedApplication
    app = DebuggedApplication(app, True)
    run_simple('localhost', 6060, app, use_reloader=True)


def emit_event(event, *args, **kwargs):
    """Emit a event and return a `EventResult` instance."""
    app = local.application
    if not app.finalized:
        raise RuntimeError('You cannot emit events before the app is set up')
    return [x(event, *args, **kwargs) for x in
            app.events.iter(event)]

class EventManager(object):
    """Helper class that handles event listeners and event emitting.

    This is *not* a public interface. Always use the `emit_event` or
    `iter_listeners` functions to access it or the `connect_event` or
    `disconnect_event` methods on the application.
    """

    def __init__(self, app):
        self.app = app
        self._listeners = {}
        self._last_listener = 0

    def connect(self, event, callback, position='after'):
        """Connect a callback to an event."""
        assert position in ('before', 'after'), 'invalid position'
        listener_id = self._last_listener
        event = intern(event)
        if event not in self._listeners:
            self._listeners[event] = deque([callback])
        elif position == 'after':
            self._listeners[event].append(callback)
        elif position == 'before':
            self._listeners[event].appendleft(callback)
        self._last_listener += 1
        return listener_id

    def remove(self, listener_id):
        """Remove a callback again."""
        for event in self._listeners:
            event.pop(listener_id, None)

    def iter(self, event):
        """Return an iterator for all listeners of a given name."""
        if event not in self._listeners:
            return iter(())
        return iter(self._listeners[event])

    def template_emit(self, event, *args, **kwargs):
        """Emits events for the template context."""
        results = []
        for f in self.iter(event):
            rv = f(*args, **kwargs)
            if rv is not None:
                results.append(rv)
        return TemplateEventResult(results)

def sibpath(path, sibling):
    return os.path.join(os.path.dirname(path), sibling)

def require_role(role):
    """Wrap a view so that it requires a given role to access."""
    def wrapped(f):
        def decorated(request, **kwargs):
            print request.user
            if request.user.role >= role:
                return f(request, **kwargs)
            raise Forbidden()
        decorated.__name__ = f.__name__
        decorated.__doc__ = f.__doc__
        return decorated
    return wrapped



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



def gettext(string, plural=None, n=1):
    """Translate something. XXX: add real translation here"""
    if plural is not None and n != 1:
        return plural
    return string

_ = gettext

def gen_pwhash(password):
    """Return a the password encrypted in sha format with a random salt."""
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    salt = gen_salt(6)
    h = sha.new()
    h.update(salt)
    h.update(password)
    return 'sha$%s$%s' % (salt, h.hexdigest())

def gen_salt(length=6):
    """Generate a random string of SALT_CHARS with specified ``length``."""
    if length <= 0:
        raise ValueError('requested salt of length <= 0')
    return ''.join(choice(SALT_CHARS) for _ in xrange(length))

def check_pwhash(pwhash, password):
    """Check a password against a given hash value. Since
    many forums save md5 passwords with no salt and it's
    technically impossible to convert this to an sha hash
    with a salt we use this to be able to check for
    plain passwords::

        plain$$default

    md5 passwords without salt::

        md5$$c21f969b5f03d33d43e04f8f136e7682

    md5 passwords with salt::

        md5$123456$7faa731e3365037d264ae6c2e3c7697e

    sha passwords::

        sha$123456$118083bd04c79ab51944a9ef863efcd9c048dd9a

    Note that the integral passwd column in the table is
    only 60 chars long. If you have a very large salt
    or the plaintext password is too long it will be
    truncated.
    """
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    if pwhash.count('$') < 2:
        return False
    method, salt, hashval = pwhash.split('$', 2)
    if method == 'plain':
        return hashval == password
    elif method == 'md5':
        h = md5.new()
    elif method == 'sha':
        h = sha.new()
    else:
        return False
    h.update(salt)
    h.update(password)
    return h.hexdigest() == hashval


class Pagination(object):
    """Pagination helper."""

    def __init__(self, endpoint, page, per_page, total, url_args=None):
        self.endpoint = endpoint
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = int(math.ceil(self.total / float(self.per_page)))
        self.url_args = url_args or {}
        self.necessary = self.pages > 1

    def generate(self, normal='<a href="%(url)s">%(page)d</a>',
                 active='<strong>%(page)d</strong>',
                 commata='<span class="commata">,\n</span>',
                 ellipsis=u'<span class="ellipsis">...\n</span>',
                 threshold=3, prev_link=False,
                 next_link=False, gray_prev_link=True, gray_next_link=True):
        from textpress.application import url_for
        was_ellipsis = False
        result = []
        prev = None
        next = None
        small_threshold = math.ceil(threshold / 2.0)
        get_link = lambda x: url_for(self.endpoint, page=x, **self.url_args)

        for num in xrange(1, self.pages + 1):
            if num == self.page:
                was_ellipsis = False
            if num - 1 == self.page:
                next = num
            if num + 1 == self.page:
                prev = num
            if num <= small_threshold or \
               num > self.pages - small_threshold or \
               abs(self.page - num) < threshold:
                if result and result[-1] != ellipsis:
                    result.append(commata)
                was_space = False
                link = get_link(num)
                template = num == self.page and active or normal
                result.append(template % {
                    'url':      link,
                    'page':     num
                })
            elif not was_ellipsis:
                was_ellipsis = True
                result.append(ellipsis)

        if next_link:
            if next is not None:
                result.append(u' <a href="%s">Next &raquo;</a>' %
                              get_link(next))
            elif gray_next_link:
                result.append(u' <span class="disabled">Next &raquo;</span>')
        if prev_link:
            if prev is not None:
                result.insert(0, u'<a href="%s">&laquo; Prev</a> ' %
                              get_link(prev))
            elif gray_prev_link:
                result.insert(0, u'<span class="disabled">&laquo; Prev</span> ')

        return u''.join(result)



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


def flash(msg, type='info'):
    """Add a message to the message flash buffer.

    The default message type is "info", other possible values are
    "add", "remove", "error", "ok" and "configure". The message type affects
    the icon and visual appearance.

    The flashes messages appear only in the admin interface!
    """
    assert type in ('info', 'add', 'remove', 'error', 'ok', 'configure')
    if type == 'error':
        msg = (u'<strong>%s:</strong> ' % _('Error')) + msg
    local.request.session.setdefault('admin/flashed_messages', []).\
            append((type, msg))


can_build_eventmap = True
def build_eventmap(app):
    """Walk through all the builtins and plugins for an application and
    look for `emit_event` calls. This is useful for plugin developers that
    want to find possible entry points without having to dig the source or
    missing documentation. Speaking of documentation: This could help for
    that too.
    """
    if not can_build_eventmap:
        raise RuntimeError('this feature requires python 2.5')
    import glashammer

    textpress_root = os.path.realpath(os.path.dirname(glashammer.__file__))
    searchpath = [(textpress_root, '__builtin__')]

    #for plugin in app.plugins.itervalues():
    #    path = os.path.realpath(plugin.path)
    #    if os.path.commonprefix([textpress_root, path]) != textpress_root:
    #        searchpath.append((plugin.path, plugin.name))

    def walk_ast(ast):
        if isinstance(ast, _ast.Call) and \
           isinstance(ast.func, _ast.Name) and \
           ast.func.id in ('emit_event', 'iter_listeners') and \
           ast.args and \
           isinstance(ast.args[0], _ast.Str):
            yield ast.args[0].s, ast.func.lineno
        for field in ast._fields or ():
            value = getattr(ast, field)
            if isinstance(value, (tuple, list)):
                for node in value:
                    if isinstance(node, _ast.AST):
                        for item in walk_ast(node):
                            yield item
            elif isinstance(value, _ast.AST):
                for item in walk_ast(value):
                    yield item

    def find_help(filename, lineno):
        help_lines = []
        lineno -= 1
        while lineno > 0:
            line = linecache.getline(filename, lineno).strip()
            if line.startswith('#!'):
                line = line[2:]
                if line and line[0] == ' ':
                    line = line[1:]
                help_lines.append(line)
            elif line:
                break
            lineno -= 1
        return '\n'.join(reversed(help_lines)).decode('utf-8')

    result = {}
    for folder, prefix in searchpath:
        offset = len(folder)
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                filename = os.path.join(dirpath, filename)
                shortname = filename[offset:]
                data = ''.join(linecache.getlines(filename))
                ast = compile(''.join(linecache.getlines(filename)),
                              filename, 'exec', 0x400)

                for event, lineno in walk_ast(ast):
                    help = find_help(filename, lineno)
                    result.setdefault(event, []).append((prefix, shortname,
                                                         lineno, help))

    return result


class NavigationItem(object):
    """An item that contains navigation information"""
    def __init__(self, title, endpoint, rule_args={}, children=[],
                 nolink=False):
        self.title = title
        self.endpoint = endpoint
        self.children = children
        self.rule_args = rule_args
        self.nolink = nolink

    def get_url(self):
        return url_for(self.endpoint, **self.rule_args)


