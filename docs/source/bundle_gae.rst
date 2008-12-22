
.. _bundle_gae:

Google Appengine Helpers
========================

This bundle provides features to help with integrating Glashammer with Google
AppEngine.

How to use
----------

During application setup::

    from glashammer.bundles.gae import setup_gae
    app.add_setup(setup_gae)

Then in your AppEngine main module::

    def main():
        gae.make_and_run_gae_app(setup)

    if __name__ == '__main__':
        main()


Available API
-------------

.. autofunction:: glashammer.bundles.gae.make_and_run_gae_app

.. autofunction:: glashammer.bundles.gae.make_gae_app

.. autofunction:: glashammer.bundles.gae.user_only_view

.. autofunction:: glashammer.bundles.gae.admin_only_view

.. autofunction:: glashammer.bundles.gae.get_gae_user

.. autofunction:: glashammer.bundles.gae.redirect_gae_login_url

