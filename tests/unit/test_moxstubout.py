# Copyright 2014 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslotest import base
from oslotest import moxstubout


class TestMoxStubout(base.BaseTestCase):

    def _stubable(self):
        pass

    def test_basic_stubout(self):
        f = self.useFixture(moxstubout.MoxStubout())
        before = TestMoxStubout._stubable
        f.mox.StubOutWithMock(TestMoxStubout, '_stubable')
        after = TestMoxStubout._stubable
        self.assertNotEqual(before, after)
        f.cleanUp()
        after2 = TestMoxStubout._stubable
        self.assertEqual(before, after2)
        f._clear_cleanups()
