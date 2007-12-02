
from unittest import TestCase

from glashammer.bundle import Bundle
from glashammer.application import BaseGlashammerSite

class BasicBundle(Bundle):
    _lifecycle_run = False

    def lifecycle(self):
        self._lifecycle_run = True


class BundleLifeTestCase(TestCase):

    def test_lifecycle_runs(self):
        b = BasicBundle(BaseGlashammerSite({}))
        assert b._lifecycle_run

    def test_register_runs_lifecycle(self):
        s = BaseGlashammerSite({})
        b = s.register_bundle(BasicBundle)
        assert b._lifecycle_run

    def test_register_registers(self):
        s = BaseGlashammerSite({})
        b = s.register_bundle(BasicBundle)
        assert b in s.bundles


        
