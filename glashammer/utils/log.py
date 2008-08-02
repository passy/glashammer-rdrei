
from logging import getLogger, debug as ldebug, \
    info as linfo, warning as lwarning, error as lerror


root_logger = getLogger('')

def add_log_handler(handler):
    root_logger.addHandler(handler)

def debug(msg):
    ldebug(msg)

    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'debug', msg)


def info(msg):
    linfo(msg)

    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'debug', msg)


def warning(msg):
    lwarning(msg)

    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'warning', msg)


def error(msg):
    lerror(msg)

    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'error', msg)


