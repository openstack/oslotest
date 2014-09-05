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


from six.moves import mock

from oslotest import base
from oslotest import mockpatch


class Foo(object):
    def bar(self):
        pass


def mocking_bar(self):
    return 'mocked!'


class TestMockPatch(base.BaseTestCase):
    def test_mock_patch_with_replacement(self):
        self.useFixture(mockpatch.Patch('%s.Foo.bar' % (__name__),
                                        mocking_bar))
        instance = Foo()
        self.assertEqual(instance.bar(), 'mocked!')

    def test_mock_patch_without_replacement(self):
        self.useFixture(mockpatch.Patch('%s.Foo.bar' % (__name__)))
        instance = Foo()
        self.assertIsInstance(instance.bar(), mock.MagicMock)


class TestMockMultiple(base.BaseTestCase):
    def test_mock_multiple_with_replacement(self):
        self.useFixture(mockpatch.Multiple('%s.Foo' % (__name__),
                                           bar=mocking_bar))
        instance = Foo()
        self.assertEqual(instance.bar(), 'mocked!')

    def test_mock_patch_without_replacement(self):
        self.useFixture(mockpatch.Multiple('%s.Foo' % (__name__),
                                           bar=mockpatch.Multiple.DEFAULT))
        instance = Foo()
        self.assertIsInstance(instance.bar(), mock.MagicMock)


class TestMockPatchObject(base.BaseTestCase):
    def test_mock_patch_object_with_replacement(self):
        self.useFixture(mockpatch.PatchObject(Foo, 'bar', mocking_bar))
        instance = Foo()
        self.assertEqual(instance.bar(), 'mocked!')

    def test_mock_patch_object_without_replacement(self):
        self.useFixture(mockpatch.PatchObject(Foo, 'bar'))
        instance = Foo()
        self.assertIsInstance(instance.bar(), mock.MagicMock)
