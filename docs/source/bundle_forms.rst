

.. _bundle_forms:

Form handling and validation
============================

Forms are validated in Glashammer using WTForms. The forms bundle in
Glashammer does not have to be used, it only helps by adding some features
that may help you in addition to WTForms.

Forms, Fields, and Validators
-----------------------------

A form has any number of fields, and each of these fields has any number of
validators. Fields are of different types that reflect the different types of
data you wish to get from the request.

Creating a form
---------------

A form should first be defined as a class with a declarative syntax like so::

    from wtforms import Form, TextField, PasswordField

    class LoginForm(Form):
        """My login form"""
        username = TextField()
        password = PasswordField()

This form contains two fields, a username and a password.

Loading a form with request form data
-------------------------------------

The form above is just a definition of the form. To make it useful, the form should instantiated and
loaded with form data.

This usually occurs during a request in a view callable, for example::

    def do_login(request):
        form = LoginForm(request.form)

Using the form instance
-----------------------

A form isntance can do a number of things. Firstly the form data passed on
construction may be validated using the :meth:`wtforms.Form.validate` method
like so::

    def do_login(request):
        form = LoginForm(request.form)
        if form.validate():
            # Form is valid
            pass

The form instance may also be used to populate a python instance, using the
:meth:`wtforms.Form.auto_populate` method. So using a slightly different
example where this might make sense::

    def do_comment(request):
        form = CommentForm(request.form)
        if form.validate():
            # Form is valid
            comment = Comment()
            form.auto_populate(comment)

Rendering form data in a template
---------------------------------

The usual pattern is to pass the form instance into the template's context
during a :func:`glashammer.utils.render_response` call like so::

    def do_comment(request):
        if request.method == 'GET':
            # it's a get, so just show the form
            form = CommentForm()
            return render_response('add_comment.html', form=form)

And thus the form instance will be available in the template.

From the template, a number of things can be accessed:


Rendering each field
~~~~~~~~~~~~~~~~~~~~

A quick rendering of each field can be performed on the form by accessing the
field by name. for example:

.. code-block:: jinja

    {{ form.username }}

This is the simple way. In reality it is actually calling the form.username() function.
Any html parameter can be passed into this call, for example:

.. code-block:: jinja

   {{ form.password(style="width: 200px;" max_length=15) }}


Rendering each field label
~~~~~~~~~~~~~~~~~~~~~~~~~~

The label for each field can also be accessed, with:

.. code-block:: jinja

    {{ form.username.label }}

Rendering an html label for use in the form.


Dict-like form access
~~~~~~~~~~~~~~~~~~~~~

Jinja2 allows you to use dict-like attribute markup, so if your field name is
a variable, you can access it like:

.. code-block:: jinja

    {{ form[field_name] }}


Complete form example
~~~~~~~~~~~~~~~~~~~~~

So, for a complete form, we might have:

.. code-block:: jinja

    <form method="post" action="">
        {{ form.username.label }} {{ form.username }}
        {{ form.password.label }} {{ form.password }}
        <input type="submit" value="Log in" />
    </form>



.. note::

    There is nothing to stop you from hand-writing your form markup, and for
    more complicated forms you certainly will have to. The validation for the
    form stays the same though, and you have a nice graded path from automatic
    generation to hand-written.



Built in field types
--------------------

Built in validators
-------------------

Complete API
------------

.. automodule:: wtforms.form
    :members:

.. automodule:: wtforms.fields
    :members:

.. automodule:: wtforms.validators
    :members:

