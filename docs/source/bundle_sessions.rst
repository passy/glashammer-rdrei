
.. _bundle_sessions:

Sessions
========

The sessions bundle provides client-side sessions safeguarded in a SecureCookie.
The session object (just a dict) can be accessed through the function
get_session().

To use a session object, treat it just as a dict. The bundle itself will decide
whether the session object has changed and thus update the cookie accordingly as
required.

Available API
-------------

.. autofunction:: glashammer.bundles.sessions.get_session

Bundle cheat-sheet
------------------

Configuration variables added

    * sessions/cookie_name
        The name of the cookie stored on the client (type: str, default: 'glashammer_session')
    * sessions/secret
        The secret used for session encrypting
