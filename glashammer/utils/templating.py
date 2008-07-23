
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def create_template_environment(searchpaths=[], globals={}, filters={}):
    env = Environment(
        loader=FileSystemLoader(searchpaths),
        extensions=['jinja2.ext.i18n']
    )
    env.globals.update(globals)
    env.filters.update(filters)
    return env
