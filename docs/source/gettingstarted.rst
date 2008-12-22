
.. _gettingstarted:

Getting Started Guide
=====================

This chapter will help you get running with Glashammer. It is only a cursory
look, and the following chapters will describe more detailed usage.

Downloading
-----------

Refer to our downloads section at:

    :ref:`downloads`


Requirements
------------


The following libraries should be installed:

* Werkzeug
* Jinja2
* WTForms

.. seealso::

   :ref:`external-references`


Your First Application
----------------------

To get started using the application instance, please refer to
examples/helloworld/__init__.py, from which this excerpt is taken::

    from glashammer import make_app, run_very_simple, Response


    def hello_view(req):
        return Response('<h1>Hello World</h1>')

    def setup(app):
        app.add_url('/', endpoint='hello/index', view=hello_view)

    if __name__ == '__main__':
        from os.path import dirname
        app =  make_app(setup, dirname(__file__))
        run_very_simple(app)

As you can see, this very simple application is composed of a single view
(just the callable hello_view), linked to an endpoint ('hello/index') and
served at a path in the web application ('/').

The application instance is created, and passed the function that will be
called during application instantiation. This setup function is the entry
point into the framework, as it allows the application instance to be
configured in a number of ways. This "configuration" happens during the
constructor of the application instance, and once it is configured, the
application is only geared to serve requests. Additional programmatic hooks
are available during the request by means of events.

You can run a debug server for this WSGI application instance using the
run_very_simple() function. This is not suitable for a production environment.

If you have downloaded the source, you can run the example above using (from
the source directory)::

    PYTHONPATH=. python examples/helloworld/run.py

This ensures that the glashammer package is available in the python path
without actually installing. Now open a browser at http://localhost:6060/
and you will be presented with the single view of the application.

The following chapters will describe features in depth.


