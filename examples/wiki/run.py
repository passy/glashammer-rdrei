# -*- coding: utf-8 -*-


from glashammer.application import declare_app
from glashammer.utils import run_very_simple, sibpath

application = declare_app(sibpath(__file__, 'app.yaml'))

if __name__ == '__main__':
    run_very_simple(application)

