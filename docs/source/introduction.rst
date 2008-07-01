Introduction
============

Glashammer is simply a Python web application development framework. Yes, yet
another one. Glashammer has lofty goals. Firstly something simple such as "hello
world" should be very simple, yet adding extra ready-components (such as an
admin interface) should also be very easy, and thus, batteries are very much
included.

Unlike a framework like Django, Glashammer is built using various proven
components. However, unlike a framework like Pylons, Glashammer decides what is
best for you in a number of situations. Choice is a great thing, and replacement
components are easy to add/replace, but the default configuration is complete.

Features
--------

* WSGI (but no WSGI knowledge needed)
* Painfully explicit
* Reusable components
* Form integration
* Database Integration
* Auth out of the box
* Admin interface for application management
* Template integration

Ready Components
----------------

The table below shows the various components used, and what they are used for:

+------------+--------------------------+
|  Library   | Use                      |
+============+==========================+
| Werkzeug   | WSGI utilities and more  |
+------------+--------------------------+
| SQLAlchemy | Database integration     |
+------------+--------------------------+
| Jinja2     | Templating               |
+------------+--------------------------+
| WTForms    | Form validation          |
+------------+--------------------------+

We have aimed to make some of these decisions for you by selecting these
components. You might hate one or more of them, in which case you could swap it out
easily enough, or just use a different framework like Pylons, which has a real
emphasis on making these things optional.

