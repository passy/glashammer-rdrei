
.. _bundle_couchdb:

CouchDB Integration
===================

This bundle provides two features:

1. A Thread local isntance of a server bound to the URL of your choosing.
2. A proxy to that Couch instance

Using CouchDB
-------------

To use the couchdb bundle add its setup function during application setup,
like so::

    from glashammer.bundles.couchdbdb import setup_couchdb

    def setup_app(app):
        app.add_setup(setup_couchdb)

This will add the bundle using the default url of `http://localhost:5984`,
and a mount pioint of `/couch` for the proxy. These default values can be
overridden on adding the setup function, and later overriden by configuration
variables::

    from glashammer.bundles.couchdbdb import setup_couchdb

    def setup_app(app):
        app.add_setup(setup_couchdb, 'http://localhost:5984', '/couchdb')

Using the server instance
-------------------------

The server instance is available to the request on the thread local instance
as the by calling the :func:`get_couchdb_server` function::

    from glashammer.bundles.couchdbdb import get_couchdb_server

    def my_view(req):
        # Get the server instance
        server = get_couchdb_server()

        # Now do something with it
        server.create('my_db')

Bundle cheat-sheet
------------------

Endpoints:
    `couchdb/proxy` For making proxy calls to the couchdb isntance

Configuration Variables:
    * `couchdb/server_url` - The couchdb server's URL
    * `couchdb/mount_path` - The path to the couchdb proxy

API:

.. autofunction:: glashammer.bundles.couchdbdb.get_couchdb_server

Setup callable arguments:

.. autofunction:: glashammer.bundles.couchdbdb.setup_couchdb




