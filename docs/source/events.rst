
.. _events:

Events
======

Events (or signals) can be fired by any part of your application, and can be
connected to by any other part. They are identified by a unique string which is
used to emit, and connect events.

You can invent your own events, and there are some builtin Glashammer events
that you can connect to.

Basic Events
------------

So, for example, say you have a piece of code in your application that handles
plain text searching and indexing, you would like to be notified when new
content is added in order to index it. The indexing code will connect an
imaginary event such as 'content-added'. It doesn't actually matter that nothing
is available to fire that event at the moment. So during application setup::

    def build_index():
        """Build some index"""

    app.connect_event('content-added', build_index)

Now later in your application, be it a blog or a wiki or something, when you
write the content add/update code, you can ensure that indexing takes place by
emitting that same event such that::

    emit_event('content-added')

These kind of simple events are useful, but they can be more useful by using
event arguments, and callback return functions.


Event Arguments
---------------

An event argument is passed to all the event handles when the event is emitted,
so for example from the Glashammer source, after a Request is created, there is
an opportunity to modify the request because the event 'request-end' is emitted
like so::

    emit_event('request-end', request)

And an event handler for this might be something like::

    def process_request(request):
        """Do something with the request"""


Event handler return functions
------------------------------

So far event handlers have not had any return values (or have returned None) and
this list of values is available to the event emitter as a list. So, for another
example from the Glashammer examples source, in a situation with pluggable
authentication, the application wished to know what authentication handlers will
authenticate a username/password combination. The event is 'check-password'. So
in the authentication provider::

    def dumb_password_checker(username, password):
        # Accept any password
        return True

    app.connect_event('check-password', dumb_password_checker)

And then in the auth bundle which would like to use these checkers::

    def check_username_password(username, password):
        results = emit_event('check-password', username, password)
        return any(results)

Thus the auth bundles has delegated checking of passwords to any other bundle
that specifically provides this behaviour.


Template events
---------------

Templates have an additional function (emit_event) for emitting events from a template, and
receiving the results in a variable type that is suitable for rendering in a
template.


Built in events
---------------

These are the built-in events for Glashammer:

    app-setup
        Emitted at the end of the application setup phase.

    request-start
        Emitted when the request is received before the urls are matched.

    request-end
        Emitted when the request has been created, and urls have been matched,
        but before the view has been called with the request.

    response-start
        Emitted when the response has been create, but not called.

    response-end
        Emitted after the response has been called, before it is returned back
        to the server to return to the client.


Additional notes
----------------

* In Glashammer, events do not need to be predefined, and so there is no dependency between event emitter and event connector. If you connect to an event that doesn't ever get emitted, your handler will never get emitted.
