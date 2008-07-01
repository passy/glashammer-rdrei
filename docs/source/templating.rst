
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
    
