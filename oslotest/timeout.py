# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import fixtures

import os


class Timeout(fixtures.Fixture):
    """Set the maximum length of time for the test to run.

    Uses OS_TEST_TIMEOUT to get the timeout.

    """

    def __init__(self, default_timeout=0, scaling_factor=1):
        super(Timeout, self).__init__()
        try:
            self._default_timeout = int(default_timeout)
        except ValueError:
            # If timeout value is invalid do not set a timeout.
            self._default_timeout = 0
        self._scaling_factor = scaling_factor

    def setUp(self):
        super(Timeout, self).setUp()
        test_timeout = os.environ.get('OS_TEST_TIMEOUT', self._default_timeout)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            # If timeout value is invalid use the default timeout.
            test_timeout = self._default_timeout
        try:
            scaled_timeout = int(test_timeout * self._scaling_factor)
        except ValueError:
            # If scaling factor is invalid, use the basic test timeout.
            scaled_timeout = test_timeout
        if scaled_timeout > 0:
            self.useFixture(fixtures.Timeout(scaled_timeout, gentle=True))
