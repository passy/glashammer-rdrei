
The Glashammer Application
==========================

Almost the entire Glashammer API is available through the application instance
that will be passed to your setup callable. To create an application object,
call glashammer.make_app().

.. autofunction:: glashammer.application.make_app(setup_func, instance_dir)

Getting Started
---------------

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

which is linked to the endpoint
    >>> def my_setup(app):
    >>>     ...
    >>> from glashammer import make_app
    >>> app = make_app(my_setup, INSTANCE)

.. autoclass:: glashammer.application.GlashammerApplication
    :members: add_setup

.. automethod:: glashammer.application.GlashammerApplication.add_setup
