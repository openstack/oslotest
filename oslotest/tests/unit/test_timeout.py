# -*- coding: utf-8 -*-

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

from oslotest import timeout


class TimeoutTestCase(testtools.TestCase):

    @mock.patch('os.environ.get')
    @mock.patch.object(timeout.Timeout, 'useFixture')
    @mock.patch('fixtures.Timeout')
    def test_timeout(self, fixture_timeout_mock, fixture_mock, env_get_mock):
        env_get_mock.return_value = 1
        tc = timeout.Timeout()
        tc.setUp()
        env_get_mock.assert_called_once_with('OS_TEST_TIMEOUT', 0)
        fixture_timeout_mock.assert_called_once_with(1, gentle=True)
        self.assertEqual(fixture_mock.call_count, 1)

    @mock.patch('os.environ.get')
    @mock.patch.object(timeout.Timeout, 'useFixture')
    @mock.patch('fixtures.Timeout')
    def test_no_timeout(self, fixture_timeout_mock, fixture_mock,
                        env_get_mock):
        # Returning 0 means we don't install the timeout
        env_get_mock.return_value = 0
        tc = timeout.Timeout()
        tc.setUp()
        env_get_mock.assert_called_once_with('OS_TEST_TIMEOUT', 0)
        self.assertEqual(fixture_timeout_mock.call_count, 0)
        self.assertEqual(fixture_mock.call_count, 0)
