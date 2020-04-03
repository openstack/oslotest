# -*- coding: utf-8 -*-

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
import os
import unittest

import fixtures
import six
from six.moves import mock
import testtools

from oslotest import base


class TestBaseTestCase(testtools.TestCase):

    class FakeTestCase(base.BaseTestCase):
        def test_fake_test(self):
            pass

    @mock.patch('os.environ.get')
    @mock.patch('oslotest.timeout.Timeout.useFixture')
    @mock.patch('fixtures.Timeout')
    def test_timeout(self, fixture_timeout_mock, fixture_mock, env_get_mock):
        env_get_mock.return_value = 1
        tc = self.FakeTestCase("test_fake_test")
        tc._set_timeout()
        env_get_mock.assert_called_once_with('OS_TEST_TIMEOUT', 0)
        fixture_timeout_mock.assert_called_once_with(1, gentle=True)
        self.assertEqual(1, fixture_mock.call_count)

    @mock.patch('os.environ.get')
    def test_fake_logs_default(self, env_get_mock):
        # without debug and log capture
        env_get_mock.side_effect = lambda value, default=None: {
            'OS_DEBUG': 0, 'OS_LOG_CAPTURE': 0}.get(value, default)
        tc = self.FakeTestCase("test_fake_test")
        tc.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        self.assertFalse(tc.log_fixture.capture_logs)
        self.assertIsNone(tc.log_fixture.logger)

    @mock.patch('os.environ.get')
    @mock.patch('logging.basicConfig')
    def test_fake_logs_with_debug(self, basic_logger_mock, env_get_mock):
        env_get_mock.side_effect = lambda value, default=None: {
            'OS_DEBUG': 'True', 'OS_LOG_CAPTURE': 0}.get(value, default)
        tc = self.FakeTestCase("test_fake_test")
        tc.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        basic_logger_mock.assert_called_once_with(format=base._LOG_FORMAT,
                                                  level=logging.DEBUG)

    @mock.patch('os.environ.get')
    @mock.patch.object(FakeTestCase, 'useFixture')
    def test_fake_logs_with_log_cap(self, fixture_mock, env_get_mock):
        env_get_mock.side_effect = lambda value: {'OS_DEBUG': 0,
                                                  'OS_LOG_CAPTURE': 'True'
                                                  }.get(value)
        tc = self.FakeTestCase("test_fake_test")
        tc.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        self.assertEqual(5, fixture_mock.call_count)

    def test_mock_patch_cleanup_on_teardown(self):
        # create an object and save its reference
        class Sub(object):
            pass

        obj = Sub()
        obj.value = obj.backup = object()

        # patch the object
        mock.patch.object(obj, 'value').start()
        self.assertNotEqual(obj.backup, obj.value)

        # run a test case
        loader = unittest.defaultTestLoader
        suite = loader.loadTestsFromTestCase(self.FakeTestCase)
        suite.run(unittest.TestResult())

        # check that mock patches are cleaned up
        self.assertEqual(obj.backup, obj.value)

    @mock.patch('os.environ')
    def test_capture_output_disabled(self, mock_env):
        mock_env.get.return_value = ''
        tc = self.FakeTestCase("test_fake_test")
        tc.setUp()
        self.assertIsNone(tc.output_fixture.stdout)
        self.assertIsNone(tc.output_fixture.stderr)

    @mock.patch('os.environ')
    def test_enabled(self, mock_env):
        mock_env.get.return_value = 'True'
        tc = self.FakeTestCase("test_fake_test")
        tc.setUp()
        self.assertIsNotNone(tc.output_fixture.stdout)
        self.assertIsNotNone(tc.output_fixture.stderr)


class TestManualMock(base.BaseTestCase):

    def setUp(self):
        # Create a cleanup to undo a patch() call *before* calling the
        # base class version of setup().
        patcher = mock.patch('os.environ.keys')
        patcher.start()
        self.addCleanup(patcher.stop)
        super(TestManualMock, self).setUp()
        self.useFixture(fixtures.MockPatch('fixtures.Timeout'))

    def test_mock_patch_manually(self):
        # Verify that if a test instance creates its own mock and
        # calls start/stop itself we don't get an error.
        patcher = mock.patch('os.environ.get')
        patcher.start()
        self.addCleanup(patcher.stop)


class TestTempFiles(base.BaseTestCase):
    def test_create_unicode_files(self):
        files = [["no_approve", u'ಠ_ಠ']]
        temps = self.create_tempfiles(files)
        self.assertEqual(1, len(temps))
        with open(temps[0], 'rb') as f:
            contents = f.read()
        self.assertEqual(u'ಠ_ಠ', six.text_type(contents, encoding='utf-8'))

    def test_create_unicode_files_encoding(self):
        files = [["embarrassed", u'⊙﹏⊙', 'utf-8']]
        temps = self.create_tempfiles(files)
        self.assertEqual(1, len(temps))
        with open(temps[0], 'rb') as f:
            contents = f.read()
        self.assertEqual(u'⊙﹏⊙', six.text_type(contents, encoding='utf-8'))

    def test_create_unicode_files_multi_encoding(self):
        files = [
            ["embarrassed", u'⊙﹏⊙', 'utf-8'],
            ['abc', 'abc', 'ascii'],
        ]
        temps = self.create_tempfiles(files)
        self.assertEqual(2, len(temps))
        for i, (basename, raw_contents, raw_encoding) in enumerate(files):
            with open(temps[i], 'rb') as f:
                contents = f.read()
            if not isinstance(raw_contents, six.text_type):
                raw_contents = six.text_type(raw_contents,
                                             encoding=raw_encoding)
            self.assertEqual(six.text_type(contents, encoding=raw_encoding),
                             raw_contents)

    def test_create_bad_encoding(self):
        files = [["hrm", u'ಠ~ಠ', 'ascii']]
        self.assertRaises(UnicodeError, self.create_tempfiles, files)

    def test_prefix(self):
        files = [["testing", '']]
        temps = self.create_tempfiles(files)
        self.assertEqual(1, len(temps))
        basename = os.path.basename(temps[0])
        self.assertTrue(basename.startswith('testing'))

    def test_wrong_length(self):
        files = [["testing"]]
        self.assertRaises(ValueError, self.create_tempfiles, files)
