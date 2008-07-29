
.. _templating:

Templating
==========

In short, templating is handled by Jinja2, which has excellent documentation,
and it is vital that you read the template designer documentation
(http://jinja.pocoo.org/2/documentation/templates) in order to use it properly.

This chapter will describe how the templates integrate into your Glashammer
application.

Adding a directory of templates
-------------------------------

Templates should live in one or more directories, and each of these directories
should be added to the application as a *search path* for templates.

For example, if you have an application package like this::

    myapp/
        __init__.py
        run.py
        templates/
            mytemplate1.html
            mytemplate2.html
            ...

the directory "templates" would need to be added to your template searchpath.
This is achieved in your application setup function like so::

    def setup(app):
        app.add_template_sarchpath('/path/to/temlates')

or, if you would like to calculate the path relative to the code (if the code
resides in run.py) you can use the sibpath function like so::

    from glashammer import sibpath

    def setup(app):
        app.add_template_searchpath(sibpath(__file__, 'templates'))

.. note:: Sibpath calculates a sibling path to whatever you give it, in this case __file__
    which is the module path.


Using a template from a view
----------------------------

A template can easily be returned from a view using the render_response
function:

.. autofunction:: glashammer.render_response

The context variables are placed in the template namespace and can be used for
whatever purpose.

For example, if our template is called "hello.html" (and the directory it
resides in has been added as a template search path::

    {# Hello Template #}
    <h1>Hello {{ name }}</h1>

This template can be loaded and rendered from a view like so::

    def hello_view(req, name):
        return render_response('hello.html', name='Ali')

This would be rendered as::

    <h1>Hello Ali</h1>


Template Globals
----------------

Variables can be added to the global template context for use in any template.
Template globals are added during the setup phase of the application using:

.. automethod:: glashammer.application.GlashammerApplication.add_template_global

A very useful pattern for this situation is to use an object that is proxied
to the local object. The actual variable may not be set at the time of
application setup, but is set during the request and is available to the
templates.

For example, a good template global might be the current user object, and this
will of course not be available during application setup. Thus we use a local
proxy like so::

    from glashammer.util import local

    app.add_template_global('user', local('user'))

Then during a request, the user attribute can be set on the local object
like::

    local.user = user

And the result will be that the 'user' variable is available in all your
templates.


Template filters
----------------

Template filters are used in templates, applied to variables, and produce some
rendered formatting for display. They are actually Jinja2 filters, but
Glashammer offers you a simple way of adding them to the application.

Essentially a template filter is just a callable, which accepts one or more
arguments. The first argument is required, and that is the variable in the
template passed to the filter.

This might be an dumb example filter for returning only the first letter of a
string::

    def first_letter_only(s):
        return s[0]

Now this would be added to you application during the application setup phase
like so::

    app.add_template_filter('first_letter_only', first_letter_only)

And then used in your template as::

    {{ foo|first_letter_only }}

Jinja comes with a number of template filters as builtins (probably more than
you ever might need) and various Glashammer bundles add others.

.. seealso::

   * http://jinja.pocoo.org/2/documentation/api#custom-filters
   * http://jinja.pocoo.org/2/documentation/templates#id2
   * http://jinja.pocoo.org/2/documentation/templates#builtin-filters
