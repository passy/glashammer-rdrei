
.. _bundle_htmlhelpers:

HTML Helpers
============

These are a series of helper functions that assist in generating HTML. They are
rather simple, and may be of use. You can use this module directly by just
importing it, or if you would like it to be available from the template
namespace, you should add the bundle's setup function during application setup
phase like so::

    from glashammer.bundles.htmlhelpers import setup_htmlhelpers

    app.add_setup(setup_htmlhelpers)

The only thing that this does is add a template global variable "h" which is the
module, and so the entire API is available.

Bundle cheat-sheet
------------------

Template global variables added
    'h': :mod:`glashammer.bundles.htmlhelpers`

Full API
--------

.. automodule:: glashammer.bundles.htmlhelpers
    :members:
