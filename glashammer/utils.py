
from werkzeug.wrappers import BaseRequest, BaseResponse
from glashammer.plugins import Registry


class Request(BaseRequest):
    """
    The concrete request object used in the WSGI application.
    It has some helper functions that can be used to build URLs.
    """
    charset = 'utf-8'

    def __init__(self, environ, url_adapter):
        BaseRequest.__init__(self, environ)
        self.url_adapter = url_adapter

    def url_for(self, endpoint, **values):
        """Create an URL to a given endpoint."""
        return self.url_adapter.build(endpoint, values)

    def external_url_for(self, endpoint, **values):
        """Create an external URL to a given endpoint."""
        return self.url_adapter.build(endpoint, values, True)


class Response(BaseResponse):
    """
    The concrete response object for the WSGI application.
    """
    charset = 'utf-8'


class RedirectResponse(Response):
    """
    A response object that redirects to a new URL.
    """

    def __init__(self, url, status=302):
        Response.__init__(self, 'page moved to %s' % url,
                          headers=[('Location', url)], status=status)


class NotFoundResponse(Response):
    """
    A response that represents a not existing resource.
    """

    def __init__(self):
        Response.__init__(self, '<h1>Page Not Found</h1>',
                          status=404, mimetype='text/html')


class TemplateResponse(Response):

    def __init__(self, site, template_name, template_kw, mimetype='text/html',
                 status=200, req=None,
                 controller=None, *args, **kw):
        self.site = site
        self.request = req
        self.controller = controller
        self.template = self.site.jinja.env.get_template(template_name)
        self.template_kw = template_kw
        Response.__init__(self, status=status, mimetype=mimetype, *args, **kw)

    def __call__(self, environ, start_response):
        self.map_adapter = self.site.routing.bind_to_environ(environ)
        self._update_template_kw()
        self.response = self.template.render(**self.template_kw)
        return Response.__call__(self, environ, start_response)

    def _update_template_kw(self):
        self.template_kw.update(dict(
            site = self.site,
            request=self.request,
            controller=self.controller,
            map_adapter=self.map_adapter,
        ))


class Prioritisable(object):

    def get_priority(self):
        return 100

