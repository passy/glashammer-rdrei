
.. _bundle_repozwho:

Repoze.who integration for authentication
=========================================

Repoze.who can be used in your application like so (for configuration files)::

    from glashammer.bundles.repozewho import setup_repozewho
    app.add_setup(setup_repozewho, configfile='/path/to/repoze/config')

The configuration file format is described in http://static.repoze.org/whodocs/

Alternatively, the setup can be passed any keyword arguments that can be passed
to the PluggableAuthenticationMiddleware constructor and the middleware will be
constructed like that.

An example is in the Glashammer test suite (tests/test_repozewho.py).

.. autofunction:: glashammer.bundles.repozewho.setup_repozewho

Bundle cheat-sheet
------------------

Middleware added: repoze.who.middleware.PluggableAuthenticationMiddleware

.. seealso::

   http://static.repoze.org/whodocs/
