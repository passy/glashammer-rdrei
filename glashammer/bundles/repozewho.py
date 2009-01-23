

def middleware_factory(app, realapp, configfile=None, **repozekw):
    if configfile is not None:
        from repoze.who.config import make_middleware_with_config
        global_config = dict(
            here = realapp.instance_dir
        )
        middleware = make_middleware_with_config(app, global_config, configfile)
    elif repozekw:
        from repoze.who.middleware import PluggableAuthenticationMiddleware
        middleware = PluggableAuthenticationMiddleware(app, **repozekw)
    else:
        raise ValueError('Must either provide a configuration file, or kw')
    return middleware


def setup_repozewho(app, configfile=None, **repozekw):
    """
    Add repoze.who support to your Glashammer application.

    Either a configuration file must be provided, or keyword arguments that will
    be passed to the PluggableAuthenticationMiddleware constructor.

    These are listed as::

        class PluggableAuthenticationMiddleware(object):
            def __init__(self, app,
                 identifiers,
                 authenticators,
                 challengers,
                 mdproviders,
                 classifier,
                 challenge_decider,
                 log_stream = None,
                 log_level = logging.INFO,
                 remote_user_key = 'REMOTE_USER',
                 ):

    And defaults will be used if arguments are missing.
    """
    app.add_middleware(middleware_factory, app, configfile, **repozekw)


