


def add_log_handler(handler):
    root_logger = getLogger('')
    root_logger.addHandler(handler)

def debug(msg):
    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'debug', msg)


def info(msg):
    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'debug', msg)


def warning(msg):
    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'warning', msg)


def error(msg):
    # Racy
    from glashammer.utils import emit_event
    emit_event('log', 'error', msg)


