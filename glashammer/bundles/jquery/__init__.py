
from glashammer.utils import sibpath

def setup_jquery(app):
    app.add_template_searchpath(sibpath(__file__, 'templates'))


setup_app = setup_jquery
