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

from six.moves import mock
import testtools

from oslotest import log


class ConfigureLoggingTestCase(testtools.TestCase):

    @mock.patch('os.environ.get')
    def test_fake_logs_default(self, env_get_mock):
        # without debug and log capture
        env_get_mock.side_effect = lambda value, default=None: {
            'OS_DEBUG': 0, 'OS_LOG_CAPTURE': 0}.get(value, default)
        f = log.ConfigureLogging()
        f.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        self.assertFalse(f.capture_logs)
        self.assertIsNone(f.logger)

    @mock.patch('os.environ.get')
    @mock.patch('logging.basicConfig')
    def test_fake_logs_with_debug(self, basic_logger_mock, env_get_mock):
        env_get_mock.side_effect = lambda value, default=None: {
            'OS_DEBUG': 'True', 'OS_LOG_CAPTURE': 0}.get(value, default)
        f = log.ConfigureLogging()
        f.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        basic_logger_mock.assert_called_once_with(
            format=log.ConfigureLogging.DEFAULT_FORMAT,
            level=logging.DEBUG)

    @mock.patch('os.environ.get')
    @mock.patch('logging.basicConfig')
    def test_fake_logs_with_warning(self, basic_logger_mock, env_get_mock):
        env_get_mock.side_effect = lambda value, default=None: {
            'OS_DEBUG': 'WARNING', 'OS_LOG_CAPTURE': 0}.get(value, default)
        f = log.ConfigureLogging()
        f.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        basic_logger_mock.assert_called_once_with(
            format=log.ConfigureLogging.DEFAULT_FORMAT,
            level=logging.WARNING)

    @mock.patch('os.environ.get')
    @mock.patch('logging.basicConfig')
    def test_fake_logs_with_trace_int(self, basic_logger_mock, env_get_mock):
        env_get_mock.side_effect = lambda value, default=None: {
            'OS_DEBUG': '5', 'OS_LOG_CAPTURE': 0}.get(value, default)
        f = log.ConfigureLogging()
        f.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        basic_logger_mock.assert_called_once_with(
            format=log.ConfigureLogging.DEFAULT_FORMAT,
            level=5)

    @mock.patch('os.environ.get')
    @mock.patch('logging.basicConfig')
    def test_fake_logs_with_debug_int(self, basic_logger_mock, env_get_mock):
        env_get_mock.side_effect = lambda value, default=None: {
            'OS_DEBUG': '10', 'OS_LOG_CAPTURE': 0}.get(value, default)
        f = log.ConfigureLogging()
        f.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        basic_logger_mock.assert_called_once_with(
            format=log.ConfigureLogging.DEFAULT_FORMAT,
            level=logging.DEBUG)

    @mock.patch('os.environ.get')
    def test_fake_logs_with_log_capture(self, env_get_mock):
        env_get_mock.side_effect = lambda value: {'OS_DEBUG': 0,
                                                  'OS_LOG_CAPTURE': 'True'
                                                  }[value]
        f = log.ConfigureLogging()
        f.setUp()
        env_get_mock.assert_any_call('OS_LOG_CAPTURE')
        env_get_mock.assert_any_call('OS_DEBUG')
        self.assertIsNotNone(f.logger)
