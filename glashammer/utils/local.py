

from werkzeug import Local, LocalManager

local = Local()
local_manager = LocalManager([local])


# Grab useful things from the local object

def url_for(endpoint, **args):
    """Get the url to an endpoint."""
    if hasattr(endpoint, 'get_url_values'):
        rv = endpoint.get_url_values()
        if rv is not None:
            endpoint, updated_args = rv
            args.update(updated_args)
    anchor = args.pop('_anchor', None)
    external = args.pop('_external', False)
    rv = local.url_adapter.build(endpoint, args,
                                 force_external=external)
    if anchor is not None:
        rv += '#' + url_quote(anchor)
    return rv

def get_request():
    return local.request

def get_app():
    return local.application
