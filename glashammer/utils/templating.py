
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def create_template_environment(searchpaths, globals, filters,
                                tests, env_kw):
    if not env_kw:
        env_kw = {}
    if 'loader' not in env_kw:
        env_kw['loader'] = FileSystemLoader(searchpaths)
    if 'extensions' not in env_kw:
        env_kw['extensions']=['jinja2.ext.i18n', 'jinja2.ext.do',
                              'jinja2.ext.loopcontrols']
    env = Environment(**env_kw)
    env.globals.update(globals)
    env.filters.update(filters)
    env.tests.update(tests)
    return env
