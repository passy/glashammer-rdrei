# -*- coding: utf-8 -*-
"""
    glashammer.bundles.i18n
    ~~~~~~~~~~~~~~~~~~~~~~~

    i18n tools for Glashammer.

    :copyright: Copyright 2008-2010, The Glashammer Authors
    :license: MIT
"""

import os
from datetime import datetime
from cgi import escape
from time import strptime
from babel import Locale, dates, UnknownLocaleError, numbers
from babel.support import Translations
from glashammer.utils import local, get_app
from glashammer.utils.lazystring import LazyString, is_lazy_string

__all__ = ['_', 'gettext', 'ngettext', 'lazy_gettext']


DATE_FORMATS = ['%m/%d/%Y', '%d/%m/%Y', '%Y%m%d', '%d. %m. %Y',
                '%m/%d/%y', '%d/%m/%y', '%d%m%y', '%m%d%y', '%y%m%d']
TIME_FORMATS = ['%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p']
_settings = dict()
_translations = {}
_js_translations = {'en': ''}


def load_translations(locale):
    """Load the translation for a locale."""
    return Translations.load(_settings['path'], [locale])


def get_translations():
    """Get the active translations or `None` if there's no request to get it
    from."""

    request = getattr(local, 'request', None)
    if request is not None:
        try:
            return request.translations
        except AttributeError:
            raise RuntimeError(
                "To use the i18n bundle you have to add the I18NRequestMixin "
                "to your Request wrapper!")


def get_js_translations(locale):
    """Returns the JavaScript translations for the given locale.
    If no such translation exists, `None` is returned.
    """
    try:
        key = str(Locale.parse(locale))
    except UnknownLocaleError:
        return None
    rv = _js_translations.get(key)
    if rv is not None:
        return rv
    fn = os.path.join(_settings['path'], key, 'LC_MESSAGES', _settings['domain'] + '.js')
    if not os.path.isfile(fn):
        return None
    f = open(fn)
    try:
        _js_translations[key] = rv = f.read()
    finally:
        f.close()
    return rv


def select_locale(choices):
    """Selects a locale."""
    enabled = set(_settings['sections'])
    for locale, quality in choices:
        try:
            locale = Locale.parse(locale, sep='-')
        except UnknownLocaleError:
            continue
        if str(locale) in enabled and \
           find_catalog(locale) is not None:
            return locale
    return Locale.parse(_settings['default_language'])


def find_catalog(locale):
    """Finds the catalog for the given locale on the path.  Returns the
    filename of the .mo file if found, otherwise `None` is returned.
    """
    catalog = os.path.join(_settings['path'], str(Locale.parse(locale)),
                             'LC_MESSAGES', _settings['domain'] + '.mo')
    if os.path.isfile(catalog):
        return catalog


def gettext(string):
    """Translate the given string to the language of the current request."""
    translations = get_translations()
    if translations is None:
        return unicode(string)
    else:
        return translations.ugettext(string)


def ngettext(singular, plural, n):
    """Translate the possible pluralized string to the language of the
    application.
    """
    translations = get_translations()

    if translations is None:
        if n == 1:
            return unicode(singular)
        return unicode(plural)
    else:
        return translations.ungettext(singular, plural, n)


def lazy_gettext(string):
    """A lazy version of `gettext`."""
    if is_lazy_string(string):
        return string
    return LazyString(gettext, string)


def format_datetime(datetime=None, format='medium'):
    """Return a date formatted according to the given pattern."""
    return _date_format(dates.format_datetime, datetime, format)


def format_date(date=None, format='medium'):
    """Return the date formatted according to the pattern."""
    return _date_format(dates.format_date, date, format)


def format_month(date=None):
    """Format month and year of a date."""
    return format_date(date, 'MMMM YY')


def format_time(time=None, format='medium'):
    """Return the time formatted according to the pattern."""
    return _date_format(dates.format_time, time, format)


def list_timezones():
    """Return a list of all timezones."""
    from pytz import common_timezones
    # XXX: translate
    result = [(x, x) for x in common_timezones]
    result.sort(key=lambda x: x[1].lower())
    return result


def list_languages():
    """Return a list of all languages we have translations for.  The
    locales are ordered by display name.  Languages without sections
    are not returned.
    """
    found = set(['en'])
    languages = [('en', Locale('en'))]
    sections = set(_settings['sections'])

    for locale in os.listdir(_settings['path']):
        try:
            l = Locale.parse(locale)
        except (ValueError, UnknownLocaleError):
            continue
        key = str(l)
        if key not in found and key in sections and \
           find_catalog(l) is not None:
            languages.append((key, l))
            found.add(key)

    languages.sort(key=lambda x: x[1].display_name.lower())
    return languages


def has_language(language):
    """Check if a language exists."""
    return language in dict(list_languages())


def has_section(language):
    """Does this language have a section?"""
    try:
        language = str(Locale.parse(language))
    except UnknownLocaleError:
        return False
    return language in _settings['sections']


def datetimeformat_filter(obj, html=True, prefixed=True):
    rv = format_datetime(obj)
    if prefixed:
        rv = _(u'on %s') % rv
    if html:
        rv = u'<span class="datetime" title="%s">%s</span>' % (
            obj.strftime('%Y-%m-%dT%H:%M:%SZ'),
            escape(rv)
        )
    return rv


def has_timezone(tz):
    """When pased a timezone as string this function checks if
    the timezone is know.
    """
    from pytz import timezone
    try:
        timezone(tz)
    except:
        return False
    return True


def parse_datetime(string):
    """Parses a string into a datetime object."""
    if string.lower() == _('now'):
        return datetime.utcnow()
    convert = lambda fmt: datetime(*strptime(string, fmt)[:7])

    # first of all try the following format because a while ago it was
    # Texpress' default format
    try:
        return convert(u'%Y-%m-%d %H:%M')
    except ValueError:
        pass

    # no go with time only, and current day
    base = datetime.utcnow()
    for fmt in TIME_FORMATS:
        try:
            val = convert(fmt)
        except ValueError:
            continue
        return base.replace(hour=val.hour, minute=val.minute,
                            second=val.second)

    # no try date + time
    def combined():
        for t_fmt in TIME_FORMATS:
            for d_fmt in DATE_FORMATS:
                yield t_fmt + ' ' + d_fmt
                yield d_fmt + ' ' + t_fmt

    for fmt in combined():
        try:
            return convert(fmt)
        except ValueError:
            pass

    raise ValueError('invalid date format')


def _date_format(formatter, obj, format):
    app = get_app()
    if app is None:
        locale = Locale('en')
    else:
        locale = app.locale
    return formatter(obj, format, locale=locale)


def on_setup_complete(app):
    global _settings

    _settings['default_language'] = app.cfg['i18n/default_language']
    _settings['sections'] = app.cfg['i18n/language_sections'].split(',')
    _settings['domain'] = app.cfg['i18n/domain']


def setup_i18n(app, locale_path=None):
    """Enabled i18n support for the glashammer application.

    :param locale_path: Path to the directory containing the localization
    files.
    """

    global _settings
    app.add_config_var('i18n/default_language', str, 'en')
    app.add_config_var('i18n/language_sections', str, 'en,de')
    app.add_config_var('i18n/domain', str, 'messages')

    app.add_template_global('_', gettext)
    app.add_template_global('gettext', gettext)
    app.add_template_global('ngettext', ngettext)
    app.add_template_filter('formatdatetime', format_datetime)
    app.add_template_filter('formatdate', format_date)
    app.connect_event('app-setup', on_setup_complete)

    _settings['path'] = locale_path

_ = gettext
setup_app = setup_i18n
