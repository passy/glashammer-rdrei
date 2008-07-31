
.. _statics:

Serving static files
====================

Directories can be added to be statically served by Glashammer. These
directories are added during the application setup phase by using:

.. automethod:: glashammer.application.GlashammerApplication.add_shared

For example, to add the directory '/var/static' to be served by Glashammer::

    app.add_shared('files', '/var/static')

Glashammer will do two things:

1. Create an endpoint called `shared/files` (which is just 'shared/' + name)
which is pointed to by a url /_shared/<filename> where the filename is the
path to the requested file.
2. Create a WSGI middleware to serve these files.

The endpoint is particularly useful for reverse lookup of files, which could
be done as::

    url_for('shared/files', filename='css/main.css')

If you wanted a url for the file /var/static/css/main.css.

Real life deployment
--------------------

In real life, it is fairly painful (and very slow) to serve static files like
this, so in a deployment situation, it is best to keep these static
directories added to Glashammer (for URL lookup) but additionally to alias the
directories in the web server so that the requests never actually reach
Glashammer.

.. seealso::

   The :ref:`gh-admin` script offers the staticaliases function that can be run
   on an application to automatically create the rules you need for your web
   server configuration.

This is an example from an Apache2 configuration illustrating how to do this
with mod_wsgi::

    Alias /_shared/files /var/static
    WSGIScriptAlias / /home/ali/my_glashammer_app.py

This will improve the performance significantly, while not forcing you to
change anything between development and deployment.

