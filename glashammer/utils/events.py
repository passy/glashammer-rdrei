# -*- coding: utf-8 -*-
"""
    glashammer.utils.events
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2007-2008 by Armin Ronacher
    :license: MIT
"""
# Events

from collections import deque

from glashammer.utils.local import local

from glashammer.utils.log import debug

def emit_event(event, *args, **kwargs):
    """Emit a event and return a `EventResult` instance."""
    app = local.application
    if event != 'log':
        debug('Emit: %s (%s)' % (event, ', '.join(map(repr, args))))
    return [x(*args, **kwargs) for x in
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


class TemplateEventResult(list):
    """A list subclass for results returned by the event listener that
    concatenates the results if converted to string, otherwise it works
    exactly like any other list.
    """

    def __init__(self, items):
        list.__init__(self, items)

    def __unicode__(self):
        return u''.join(map(unicode, self))

    def __str__(self):
        return unicode(self).encode('utf-8')

