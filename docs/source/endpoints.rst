
.. _endpoints:

Rules, endpoints and views
==========================

The application is generally made up of these three things:

* Rules
* Endpoints
* Views


Rules and Endpoints
-------------------

An endpoint is a target in the application, and rules bind actual URL's to these
endpoints. Endpoints can be whatever you like, but we generally use strings in
our examples. For example, a contact application might have the following
endpoints::

    'contact/list', 'contact/edit', ...

A rule for the first endpoint might point to the url for example::

    '/contact'

And thus in the application will know that the URL /contacts and the endpoint
'contact/list' are linked.

A rule also has the ability to define implicit variables and conversions in
urls. This is directly from werkzeug.routing,
(http://werkzeug.pocoo.org/documentation/routing) except you will not have to
make rules and maps for yourself, just to specify what they should do.

So a rule with a variable (for the second endpoint, above, since we will want to
know which cntact to edit) might be::

    '/contact/<int:contact_id>'

And thus when the url such as /contact/23 is accessed in your application, the
'23' will be validated and converted into an integer and passed to whatever you
have decided to do with that endpoint.

So, for a real example using an application setup function::

    def setup(app):
        app.add_rule('/contact', 'contact/list')
        app.add_rule('/contact/<int:contact_id>', 'contact/edit')

The endpoints above have been linked with the rules above.

Reverse lookup of URLs
----------------------

The beauty of the endpoint/url system is that urls can be looked up from the
endpoint. In this way a url will always be correct relative to where the site
lives etc. This is achieved using the url_for function:

.. autofunction glashammer.url_for

For example::

    url_for('contact/edit', contact_id=4)

will give us::

    /contact/edit/4

In our scheme above.

Adding a complete map
---------------------

Because rules bound to a map cannot then be moved to another map, if you have
a pre-existing werkzeug.routing.Map isntance that you wish to use in your
glashammer application, you should pass it as the named argument url_map to
the make_app function.

Views
-----

Linking urls to endpoints is fine, but what should we actually do with the
endpoints. Views are callables which are called for an endpoint and passed the
arguments that are given in the rule. They are expected to return a Response
object (or in reality any WSGI application), which will be called to create an
actual http response.

Here is the simplest of views::

    from glashammer Response

    def hello_world_view(req):
        return Response('<h1>Hello World</h1>')


The Response object takes a string as its first argument and will render that
when returned from the view will be rendered.

The view can be linked to an endpoint in one of two ways::

    def setup(app):
        app.add_url('/', 'hello/index')
        app.add_view('hello/index', hello_world_view)

or for convenience::

    def setup(app):
        app.add_url('/', 'hello/index', view=hello_world_view)

Since in many cases you will want to set up the URL, the endpoint and the view
all in one go.

Using this, your Glashammer application will know which view to dispatch to from
a url.

Any additional arguments that are specified in the rule are passed to the view
callable. Using the endpoint example above::

    from glashammer import Response

    def contact_edit_view(req, contact_id):
        # fetch the contact from the database or do something simple:
        return Response('<h1>Contact: %s</h1>' % contact_id)

    def setup(app):
        app.add_url('/contact/edit/<int:contact_id>', 'contact/edit',
                    view=contact_edit_view)

Note that you can make this argument optional in the view by providing a default
argument to the function, and thus use the same view for many endpoints.

Adding related views as a controller
------------------------------------

A controller, or "view controller" if we want to be explicit is a container,
either module, or isntance, which contains a number of views which will be
available for a single endpoint's base.

.. automethod:: glashammer.application.GlashammerApplication.add_views_controller

