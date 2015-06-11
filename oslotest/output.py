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

import os

import fixtures

_TRUE_VALUES = ('True', 'true', '1', 'yes')


class CaptureOutput(fixtures.Fixture):
    """Optionally capture the output streams.

    The behavior is managed through two environment variables. If
    ``OS_STDOUT_CAPTURE`` is true then stdout is captured and if
    ``OS_STDERR_CAPTURE`` is true then stderr is captured.

    "True" values include ``True``, ``true``, ``1``, and ``yes``.

    .. py:attribute:: stdout

       The ``stream`` attribute from a :class:`StringStream` instance
       replacing stdout.

    .. py:attribute:: stderr

       The ``stream`` attribute from a :class:`StringStream` instance
       replacing stderr.

    """

    def __init__(self):
        super(CaptureOutput, self).__init__()
        self.stdout = None
        self.stderr = None

    def setUp(self):
        super(CaptureOutput, self).setUp()
        if os.environ.get('OS_STDOUT_CAPTURE') in _TRUE_VALUES:
            self._stdout_fixture = fixtures.StringStream('stdout')
            self.stdout = self.useFixture(self._stdout_fixture).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        if os.environ.get('OS_STDERR_CAPTURE') in _TRUE_VALUES:
            self._stderr_fixture = fixtures.StringStream('stderr')
            self.stderr = self.useFixture(self._stderr_fixture).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', self.stderr))
