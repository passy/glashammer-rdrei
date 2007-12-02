
from unittest import TestCase

from glashammer.bundle import Bundle
from glashammer.controller import Controller, ControllerBundle
from glashammer.application import BaseGlashammerSite, GlashammerSite

class SimpleController(Controller):
    pass

class SimpleBundle(Bundle):

    def lifecycle(self):
        self.register_controller('simple', SimpleController)


class TestControllerBundle(TestCase):

    def test_manual_register(self):
        s = BaseGlashammerSite({})
        b = ControllerBundle(s)
        b.register('simple', SimpleController)
        assert 'simple' in b.controllers
        assert b.controllers['simple'] is SimpleController

    def test_bundle_register(self):
        s = GlashammerSite({})
        s.register_bundle(SimpleBundle)
        assert 'simple' in s.controller.controllers
        assert s.controller.controllers['simple'] is SimpleController
        
        

