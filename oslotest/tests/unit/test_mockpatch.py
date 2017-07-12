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

import fixtures

from oslotest import base


class TestMockPatchSymbols(base.BaseTestCase):
    def test_reference(self):
        # Applications expect these public symbols to be available until the
        # deprecated module is removed.
        self.assertTrue(fixtures.MockPatchObject)
        self.assertTrue(fixtures.MockPatch)
        self.assertTrue(fixtures.MockPatchMultiple)
