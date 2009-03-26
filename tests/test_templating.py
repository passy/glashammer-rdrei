
from glashammer import make_app

def _setup(app):
    pass

def test_template_kw():
    app = make_app(_setup)
    assert not app.template_env.trim_blocks
    app = make_app(_setup, template_env_kw={'trim_blocks': True})
    assert app.template_env.trim_blocks

