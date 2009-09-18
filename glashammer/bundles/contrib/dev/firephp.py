
# adapted from http://code.cmlenz.net/diva/browser/trunk/diva/ext/firephp.py
# (c) 2008 C. M. Lenz, Glashammer Developers

from time import time
from logging import Handler

from simplejson import dumps

from glashammer.utils import local
from glashammer.utils.log import add_log_handler


LEVEL_MAP = {'DEBUG': 'LOG', 'WARNING': 'WARN', 'CRITICAL': 'ERROR'}
PREFIX = 'X-FirePHP-Data-'

def init_firephp():
    # one-time initialisation per request
    local.firephp_log = []

def inject_firephp_headers(response):
    prefix = PREFIX
    if not hasattr(response, 'headers'):
        # an httpexception or some other weird response
        return
    for i, record in enumerate(local.firephp_log):
        if i == 0:
            response.headers[prefix + '100000000001'] = '{'
            response.headers[prefix + '300000000001'] = '"FirePHP.Firebug.Console":['
            response.headers[prefix + '399999999999'] = ',["__SKIP__"]],'
            response.headers[prefix + '999999999999'] = '"__SKIP__":"__SKIP__"}'
        secs = str(int(time()))[-3:]
        msgid = '3' + secs + ('%08d' % (i + 2))
        msg = dumps(record)
        if i != 0:
            msg = ',' + msg
        response.headers[PREFIX + msgid] = msg


def emit(level, record):
    try:
        local.firephp_log.append((LEVEL_MAP.get(level.upper()), record))
    except AttributeError:
        pass


def setup_firephp(app):
    app.connect_event('wsgi-call', init_firephp)
    app.connect_event('response-start', inject_firephp_headers)
    app.connect_event('log', emit)

setup_app = setup_firephp
