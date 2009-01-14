
.. _bundle_auth:

.. note::

   The authentication system is being replaced by repoze.who integration, and
   will become depracated in later releases of Glashammer. Please see
   `bundle_repozwho`.

Authentication
==============

The authentication system shipped with Glashammer is very simple, and very easy
to extend. Essentially it splits authentication up into 3 sections:

1. Checking credentials
2. Storing user information
3. Protecting views

The authentication bundle only deals with bringing the various components that
you choose together. It's remit is merely adding a token that is unique per user
(such as a username) to the request's local variable. This token should then be
used by other implementors to store user information (say in a database).

The token itself is stored in a secure cookie on the client, which can be
decrypted, but never modified.

How to use
----------

During application setup::

    from glashammer.bundles.auth import setup_auth
    app.add_setup(setup_auth)

An additional argument can be passed to the setup function, which determines
whether views are created at /login and /logout.

.. autofunction:: glashammer.bundles.auth.setup_auth

Available API
-------------

The session can be manually logged in by calling the login method:

.. autofunction:: glashammer.bundles.auth.login

And logged out by using the logout function:

.. autofunction:: glashammer.bundles.auth.logout

Password Checking
-----------------

Password checking is a service that should be provided by connecting the
'password-check' event. (see the :ref:`events` documentation for how this
works). The password check event passes a username and password (as a
credential) to all callables connected to the event.

A True return from any of the event handlers will indicate that the credentials
were correct, and that the user should be logged in.

The bundle has a reference implementation for doing this in a view, but can very
easily be replaced and done manually.


View Decorators
---------------

The decorator auth_protected_view is provided whch will check the request for an
authorized user.

.. autofunction:: glashammer.bundles.auth.auth_protected_view


Bundle cheat-sheet
------------------

Dependent bundles loaded
    * :ref:`bundle_sessions`

Configuration variables added
    * auth/token_key
        The key used in the session to store the token key
        (type: str, default: 'auth_session_key')

Template searchpath added
    * glashammer/bundles/auth/templates

Urls Added (only if add_auth_views=True)

    * /login (endpoint: auth/login)
    * /logout (endpoint: auth/logout)

Views Added (only if add_auth_views=True)

    * view_login (endpoint: auth/login)
    * view_logout (endpoint: auth/logout)

