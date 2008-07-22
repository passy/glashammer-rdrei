
import os, string, sha, math, linecache, _ast
from collections import deque
from random import choice, randrange, random


from werkzeug import run_simple, Request as wzRequest, \
    Response as wzResponse, ClosingIterator, Local, LocalManager, redirect, \
    escape
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
    tzinfo = None#pytz.timezone(str(cfg['timezone']))
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


class Request(wzRequest):
    """The used request class."""

    def __init__(self, app, environ):
        wzRequest.__init__(self, environ)
        self.app = app


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


