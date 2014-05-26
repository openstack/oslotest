# Copyright 2014 Deutsche Telekom AG
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

import logging
import unittest

import mock
import testtools

from oslotest import base


class TestBaseTestCase(testtools.TestCase):
    class FakeTestCase(base.BaseTestCase):
        def test_fake_test(self):
            pass

    @mock.patch('os.environ.get')
    @mock.patch.object(FakeTestCase, 'useFixture')
    @mock.patch('fixtures.Timeout')
    def test_timeout(self, fixture_timeout_mock, fixture_mock, env_get_mock):
        env_get_mock.return_value = 1
        tc = self.FakeTestCase("test_fake_test")
        tc._set_timeout()
        env_get_mock.assert_called_once_with('OS_TEST_TIMEOUT', 0)
        fixture_timeout_mock.assert_called_once_with(1, gentle=True)
        self.assertEqual(fixture_mock.call_count, 1)

    @mock.patch('os.environ.get')
    @mock.patch.object(FakeTestCase, 'useFixture')
    def test_fake_logs_default(self, fixture_mock, env_get_mock):
        # without debug and log capture
        env_get_mock.side_effect = lambda value: {'OS_DEBUG': 0,
                                                  'OS_LOG_CAPTURE': 0}[value]
        tc = self.FakeTestCase("test_fake_test")
        tc._fake_logs()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_calls('OS_DEBUG')
        self.assertEqual(fixture_mock.call_count, 0)

    @mock.patch('os.environ.get')
    @mock.patch('logging.basicConfig')
    def test_fake_logs_with_debug(self, basic_logger_mock, env_get_mock):
        env_get_mock.side_effect = lambda value: {'OS_DEBUG': 'True',
                                                  'OS_LOG_CAPTURE': 0}[value]
        tc = self.FakeTestCase("test_fake_test")
        tc._fake_logs()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_calls('OS_DEBUG')
        basic_logger_mock.assert_called_once_with(format=base._LOG_FORMAT,
                                                  level=logging.DEBUG)

    @mock.patch('os.environ.get')
    @mock.patch.object(FakeTestCase, 'useFixture')
    def test_fake_logs_with_log_cap(self, fixture_mock, env_get_mock):
        env_get_mock.side_effect = lambda value: {'OS_DEBUG': 0,
                                                  'OS_LOG_CAPTURE': 'True'
                                                  }[value]
        tc = self.FakeTestCase("test_fake_test")
        tc._fake_logs()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_calls('OS_DEBUG')
        self.assertEqual(fixture_mock.call_count, 1)

    def test_mock_patch_cleanup_on_teardown(self):
        # create an object and save its reference
        class Sub(object):
            pass

        obj = Sub()
        obj.value = obj.backup = object()

        # patch the object
        mock.patch.object(obj, 'value').start()
        self.assertNotEqual(obj.value, obj.backup)

        # run a test case
        loader = unittest.defaultTestLoader
        suite = loader.loadTestsFromTestCase(self.FakeTestCase)
        suite.run(unittest.TestResult())

        # check that mock patches are cleaned up
        self.assertEqual(obj.value, obj.backup)
