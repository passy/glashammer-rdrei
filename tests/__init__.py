
import os, shutil


def setup():
    try:
        shutil.rmtree('test_output')
    except OSError:
        pass
    os.mkdir('test_output')


def teardown():
    shutil.rmtree('test_output')

