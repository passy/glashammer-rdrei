
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def create_template_environment(searchpaths=[]):
    template_env = Environment(
        loader=FileSystemLoader(searchpaths)
    )
    return template_env
