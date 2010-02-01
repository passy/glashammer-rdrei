# -*- coding: utf-8 -*-
"""
glashammer.utils.lazysettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lazy descriptor.

:copyright: 2009, The Glashammer Authors
:license: MIT
"""


class LazySettings(object):
    """A lazy settings store that is filled on application setup. Works as a
    descriptor."""

    def __init__(self, application=None):
        """Accepts an application. Can be bound later with bind()."""
        self.application = application

    def bind(self, application):
        self.application = application

    def __getitem__(self, name):
        try:
            value = self.application.cfg[name]
        except AttributeError:
            raise RuntimeError("Application setup did not complete.")
        except KeyError:
            raise RuntimeError("Configuration was not set up properly. Key %r"
                               " not found!" % name)

        return value
