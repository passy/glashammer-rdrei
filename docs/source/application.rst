
.. _application:

Setting up an application
=========================

An application instance is configured during it's constructor. It is
configuredwith the use of "setup callables". One setup callable is required
for an application, and this is called when the application is created.

It is during this phase of creation that additional components should be added
to the application, as once it is created it is nearly frozen to configuration
changes.

Examples of these types of "configuration change" are:

* Adding configuration variables
* Adding template directories, variables, and filters
* Adding urls
* Adding WSGI middleware

These all occur on an interface provided by the application instance that is
passed to the setup callable.

Back to our very first example, but with annotations::

    def setup_app(app):
        """
        I am the main application setup callable.

        I am called during the instantiation of the application and am passed
        the application. I can do various things, but in this case, I am
        adding the directory 'mytemplates' as a searchpath for templates.
        """
        app.add_template_searchpath('mytemplates')

    app = make_app(setup_app)
    # Run your application however you like. (we use the debug server)
    run_very_simple(app)

So that's how we add a template search path, but what else? Well the generated API is
below, but all these are regarded in more detail in subsequent chapters.


