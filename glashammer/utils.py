

from collections import deque

from werkzeug import run_simple, Request, Response as wzResponse, ClosingIterator, Local, LocalManager

local = Local()
local_manager = LocalManager([local])


def render_template(template_name, _stream=False, **context):
    #emit_event('before-render-template', template_name, _stream, context)
    tmpl = local.application.template_env.get_template(template_name)
    if _stream:
        return tmpl.stream(context)
    return tmpl.render(context)

def render_response(template_name, mimetype='text/html', **context):
    return Response(
        render_template(template_name, **context),
        mimetype=mimetype
    )


class Response(wzResponse):
    default_mimetype = 'text/html'

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



