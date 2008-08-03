
.. _bundle_i18n:

Internationalization
====================

Glashammer provides internationalization out of the box using the Babel
library. You can enable it by adding the i18n bundle during application
setup::

    from glashammer.bundles.i18n import setup_i18n
    app.add_setup(setup_i18n)

The language is decided by the configuration variable 'language'.


Formatting Dates in Templates
-----------------------------

The i18n bundle provides two template filters which format dates, or datetimes
into the locale's current format. These filters accept an additional argument
which is the format type ('short', 'medium', 'long'; default is 'medium') and so
can be used in a template like so for a date object::

    {{ d|formatdate('long') }}

For API for the actual functions, if you want or need to use them outside
templates are as so:

.. autofunction:: glashammer.bundles.i18n.format_datetime

.. autofunction:: glashammer.bundles.i18n.format_date


Bundle cheat-sheet
------------------

External Dependencies
    * Babel (http://babel.edgewall.org/)

Configuration variables added
    * language (type: str, default: 'en')

Template filters added
    * formatdatetime
        format a datetime object to the current language
    * formatdate
        format a date object to the current language


Full API
--------

.. automodule:: glashammer.bundles.i18n
   :members:

