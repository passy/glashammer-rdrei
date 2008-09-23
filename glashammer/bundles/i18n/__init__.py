# -*- coding: utf-8 -*-
"""
    glashammer.bundles.i18n
    ~~~~~~~~~~~~~~~~~~~~~~~

    i18n tools for Glashammer.

    :copyright: Copyright 2008 by Armin Ronacher.
    :license: MIT
    """
import os
from datetime import datetime
from time import strptime
from babel import Locale, dates, UnknownLocaleError
from babel.support import Translations

from glashammer.utils import get_app

__all__ = ['_', 'gettext', 'ngettext']


DATE_FORMATS = ['%m/%d/%Y', '%d/%m/%Y', '%Y%m%d', '%d. %m. %Y',
                '%m/%d/%y', '%d/%m/%y', '%d%m%y', '%m%d%y', '%y%m%d']
TIME_FORMATS = ['%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p']


def load_translations(locale):
    """Load the translation for a locale."""
    return Translations.load(os.path.dirname(__file__), [locale])


def gettext(string):
    """Translate the given string to the language of the application."""
    app = get_app()
    if app is None:
        return string
    return app.translations.ugettext(string)


def ngettext(singular, plural, n):
    """Translate the possible pluralized string to the language of the
    application.
    """
    app = get_app()
    if app is None:
        if n == 1:
            return singular
        return plrual
    return app.translations.ungettext(singular, plural, n)

class _TranslationProxy(object):
    """Class for proxy strings from gettext translations.  This is a helper
    for the lazy_* functions from this module.

    The proxy implementation attempts to be as complete as possible, so that
    the lazy objects should mostly work as expected, for example for sorting.
    """
    __slots__ = ('_func', '_args')

    def __init__(self, func, *args):
        self._func = func
        self._args = args

    value = property(lambda x: x._func(*x._args))

    def __contains__(self, key):
        return key in self.value

    def __nonzero__(self):
        return bool(self.value)

    def __dir__(self):
        return dir(unicode)

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return unicode(self.value)

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __mod__(self, other):
        return self.value % other

    def __rmod__(self, other):
        return other % self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __getattr__(self, name):
        if name == '__members__':
            return self.__dir__()
        return getattr(self.value, name)

    def __getitem__(self, key):
        return self.value[key]

    def __repr__(self):
        try:
            return 'i' + repr(unicode(self.value))
        except:
            return '<%s broken>' % self.__class__.__name__


def lazy_gettext(string):
    """A lazy version of `gettext`."""
    return _TranslationProxy(gettext, string)

def format_datetime(datetime=None, format='medium'):
    """Return a date formatted according to the given pattern."""
    return _date_format(dates.format_datetime, datetime, format)

def format_system_datetime(datetime=None, rebase=True):
    """Formats a system datetime.  This is the format the admin
    panel uses by default.  (Format: YYYY-MM-DD hh:mm and in the
    user timezone unless rebase is disabled)
    """
    if rebase:
        datetime = to_blog_timezone(datetime)
    return u'%d-%02d-%02d %02d:%02d' % (
        datetime.year,
        datetime.month,
        datetime.day,
        datetime.hour,
        datetime.minute
    )

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
    """Return a list of all languages."""
    app = get_app()
    if app:
        locale = app.locale
    else:
        locale = Locale('en')

    languages = [('en', Locale('en').get_display_name(locale))]
    folder = os.path.dirname(__file__)

    for filename in os.listdir(folder):
        if filename == 'en' or not \
           os.path.isdir(os.path.join(folder, filename)):
            continue
        try:
            l = Locale.parse(filename)
        except UnknownLocaleError:
            continue
        languages.append((str(l), l.get_display_name(locale)))

    languages.sort(key=lambda x: x[1].lower())
    return languages


def has_language(language):
    """Check if a language exists."""
    return language in dict(list_languages())


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
    cfg = get_app().cfg

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


_ = gettext

# Here beginneth the pluging in process

def on_setup_complete(app):
    lang = app.conf['language']
    app.locale = Locale(app.cfg['language'])
    app.translations = load_translations(app.locale)
    app.template_env.install_gettext_translations(app.translations)

def setup_i18n(app):
    app.add_config_var('language', str, 'en')
    app.add_template_filter('formatdatetime', format_datetime)
    app.add_template_filter('formatdate', format_date)
    app.connect_event('app-setup', on_setup_complete)

setup_app = setup_i18n
