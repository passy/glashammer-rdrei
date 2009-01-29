
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def create_template_environment(searchpaths=[], globals={}, filters={}, tests={}):
    env = Environment(
        loader=FileSystemLoader(searchpaths),
        extensions=['jinja2.ext.i18n', 'jinja2.ext.do',
                    'jinja2.ext.loopcontrols']
    )
    env.globals.update(globals)
    env.filters.update(filters)
    env.tests.update(tests)
    return env
