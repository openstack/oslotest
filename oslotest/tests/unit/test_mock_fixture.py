# Copyright 2017 Cloudbase Solutions Srl
# All Rights Reserved.
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

import mock
import testtools

from oslotest import mock_fixture

# NOTE(claudiub): this needs to be called before any mock.patch calls are
# being done, and especially before the test class loads. This fixes
# the mock.patch autospec issue:
# https://github.com/testing-cabal/mock/issues/396
# TODO(claudiub): Remove this once the fix has been merged and released.
mock_fixture.patch_mock_module()


class Foo(object):
    def bar(self, a, b, c, d=None):
        pass

    @classmethod
    def classic_bar(cls, a, b, c, d=None):
        pass

    @staticmethod
    def static_bar(a, b, c, d=None):
        pass


class MockSanityTestCase(testtools.TestCase):

    def setUp(self):
        super(MockSanityTestCase, self).setUp()
        self.useFixture(mock_fixture.MockAutospecFixture())

    def _check_autospeced_foo(self, foo):
        for method_name in ['bar', 'classic_bar', 'static_bar']:
            mock_method = getattr(foo, method_name)

            # check that the methods are callable with correct args.
            mock_method(mock.sentinel.a, mock.sentinel.b, mock.sentinel.c)
            mock_method(mock.sentinel.a, mock.sentinel.b, mock.sentinel.c,
                        d=mock.sentinel.d)
            mock_method.assert_has_calls([
                mock.call(mock.sentinel.a, mock.sentinel.b, mock.sentinel.c),
                mock.call(mock.sentinel.a, mock.sentinel.b, mock.sentinel.c,
                          d=mock.sentinel.d)])

            # assert that TypeError is raised if the method signature is not
            # respected.
            self.assertRaises(TypeError, mock_method)
            self.assertRaises(TypeError, mock_method, mock.sentinel.a)
            self.assertRaises(TypeError, mock_method, a=mock.sentinel.a)
            self.assertRaises(TypeError, mock_method, mock.sentinel.a,
                              mock.sentinel.b, mock.sentinel.c,
                              e=mock.sentinel.e)

        # assert that AttributeError is raised if the method does not exist.
        self.assertRaises(AttributeError, getattr, foo, 'lish')

    def _check_mock_autospec_all_members(self, mock_cls):
        for spec in [Foo, Foo()]:
            foo = mock_cls(autospec=spec)
            self._check_autospeced_foo(foo)
            self._check_autospeced_foo(foo())

    def test_mock_autospec_all_members(self):
        self._check_mock_autospec_all_members(mock.Mock)

    def test_magic_mock_autospec_all_members(self):
        self._check_mock_autospec_all_members(mock.MagicMock)

    @mock.patch.object(Foo, 'static_bar')
    @mock.patch.object(Foo, 'classic_bar')
    @mock.patch.object(Foo, 'bar')
    def test_patch_autospec_class(self, mock_meth, mock_cmeth, mock_smeth):
        foo = Foo()
        self._check_autospeced_foo(foo)

    def test_patch_autospec_multiple(self):
        with mock.patch.multiple(Foo, bar=mock.DEFAULT,
                                 classic_bar=mock.DEFAULT,
                                 static_bar=mock.DEFAULT):
            foo = Foo()
            self._check_autospeced_foo(foo)

    @mock.patch.object(Foo, 'static_bar', autospec=False)
    @mock.patch.object(Foo, 'classic_bar', autospec=False)
    @mock.patch.object(Foo, 'bar', autospec=False)
    def test_patch_autospec_class_false(self, mock_meth, mock_cmeth,
                                        mock_smeth):
        foo = Foo()
        # we're checking that method signature is not enforced.
        foo.bar()
        mock_meth.assert_called_once_with()
        foo.classic_bar()
        mock_cmeth.assert_called_once_with()
        foo.static_bar()
        mock_smeth.assert_called_once_with()

    @mock.patch.object(Foo, 'lish', create=True)
    def test_patch_create(self, mock_lish):
        foo = Foo()

        foo.lish()
        mock_lish.assert_called_once_with()
