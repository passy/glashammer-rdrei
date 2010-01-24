# -*- coding: utf-8 -*-
"""
glashammer.utils.viewfinder
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Registry for views and controllers, utilized by :mod:`glashammer.application`.

:copyright: 2009, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""


from glashammer.utils import emit_event
from functools import wraps

class ViewFinder(object):
    """Finds a view or a controller action based on its endpoint."""

    def __init__(self):
        self.views = {}
        self.controllers = {}

    def add(self, endpoint, view):
        """Register a view for an endpoint."""

        self.views[endpoint] = view

    def add_controller(self, endpoint_base, controller):
        """Register a controller instance which contains functions
        (actions) that behave like a view except for the instance context."""

        self.controllers[endpoint_base] = controller

    def find(self, endpoint):
        """Find a view for an endpoint.

        Checks views first, then controllers.  Returns the callable,
        or None when no view is found.
        """

        view = self.find_view(endpoint)

        if view is not None:
            return view

        if '/' in endpoint or '.' in endpoint:
            return self.find_controller(endpoint)

    def find_view(self, endpoint):
        """Finds a view, not a controller based on the endpoint."""

        view = self.views.get(endpoint, None)

        if hasattr(view, '__call__'):
            emit_event('view-match', view)
            return view

        return None

    def find_controller(self, endpoint):
        """Finds a controller based on its endpoint."""

        base, target = self._split_controller_endpoint(endpoint)
        controller = self.controllers.get(base)
        target = self._get_full_controller_target(controller, target)
        return self._get_controller_view(controller, target)

    def _split_controller_endpoint(self, endpoint):
        """Returns a tuple of base and target. Seperator is either a forward
        slash in the endpoint or if not found a dot."""

        split = '.'

        if '/' in endpoint:
            split = '/'

        return endpoint.split(split, 1)

    def _get_full_controller_target(self, controller, target):
        """Get the full controller target based on an optional 'target_prefix'
        attribute in the controller instance."""

        target_prefix = getattr(controller, 'target_prefix', '')
        return target_prefix + target

    def _get_controller_view(self, controller, target):
        """Get the view function from the controller instance specified by the
        full target string."""

        if hasattr(controller, target):
            emit_event('controller-match', controller, target)
            view = getattr(controller, target)
            return self._get_controller_before_wrapper(controller, view)

    def _get_controller_before_wrapper(self, controller, view):
        """Looks for a __before__ method in controller and creates a wrapper
        around it if one is found. This causes __before__ to be called prior
        to the actual view method. If not found, ``view`` is returned."""

        before = getattr(controller, '__before__', None)

        if before:
            emit_event('before-match', controller, before, view)

            def _wrap(before, view):
                @wraps(view)
                def _inner(request, **values):
                    before(request)
                    return view(request, **values)
                return _inner

            return _wrap(before, view)

        return view

