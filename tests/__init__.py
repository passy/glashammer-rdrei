
import os, shutil
from glashammer.application import make_app

def setup():
    try:
        shutil.rmtree('test_output')
    except OSError:
        pass
    os.mkdir('test_output')


def teardown():
    shutil.rmtree('test_output')

def gh_app(setup):
    return make_app(setup, 'test_output')

