# -*- coding: utf-8 -*-
"""
glashammer.bundles.i18n.request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adds i18n functionality to the request objects.

:copyright: 2010, The Glashammer Authors
:license: MIT
"""

from glashammer.bundles.i18n import select_locale, load_translations, \
        has_section, Locale
from werkzeug.utils import cached_property


class I18NRequestMixin(object):
    """A mixing that adds methods to the request to detect the current
    locale."""

    _locale = None

    def _get_locale(self):
        """The locale of the incoming request.  If a locale is unsupported, the
        default english locale is used.  If the locale is assigned it will be
        stored in the session so that that language changes are persistent.
        """
        if self._locale is not None:
            return self._locale
        rv = self.session.get('locale')
        if rv is not None:
            rv = Locale.parse(rv)
            # we could trust the cookie here because it's signed, but we do not
            # because the configuration could have changed in the meantime.
            if not has_section(rv):
                rv = None
        if rv is None:
            rv = select_locale(self.accept_languages)
        self._locale = rv
        return rv

    def _set_locale(self, locale):
        self._locale = Locale.parse(locale)
        self.__dict__.pop('translations', None)
        self.session['locale'] = str(self._locale)

    locale = property(_get_locale, _set_locale)
    del _get_locale, _set_locale

    @cached_property
    def translations(self):
        """The translations for this request."""
        return load_translations(self.locale)

