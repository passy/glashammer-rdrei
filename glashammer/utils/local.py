

from werkzeug import Local, LocalManager

local = Local()
local_manager = LocalManager([local])


# Grab useful things from the local object

def url_for(endpoint, **args):
    """Get the url to an endpoint."""
    anchor = args.pop('_anchor', None)
    external = args.pop('_external', False)
    rv = local.url_adapter.build(endpoint, args,
                                 force_external=external)
    if anchor is not None:
        rv += '#' + url_quote(anchor)
    return rv

def get_request():
    """Get the currently running request"""
    return local.request

def get_app():
    """Get the currently running applications"""
    return local.application
