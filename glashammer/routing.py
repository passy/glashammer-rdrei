
from werkzeug.routing import Map, Rule

def create_map(*rules, **kw):
    return Map(rules, **kw)

