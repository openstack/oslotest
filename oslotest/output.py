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

    The behavior is managed through arguments to the constructor. The
    default behavior is controlled via two environment variables. If
    ``OS_STDOUT_CAPTURE`` is true then stdout is captured and if
    ``OS_STDERR_CAPTURE`` is true then stderr is captured.

    "True" values include ``True``, ``true``, ``1``, and ``yes``.

    :param do_stdout: Whether to capture stdout.
    :type do_stdout: bool
    :param do_stderr: Whether to capture stderr.
    :type do_stderr: bool

    .. py:attribute:: stdout

       The ``stream`` attribute from a :class:`StringStream` instance
       replacing stdout.

    .. py:attribute:: stderr

       The ``stream`` attribute from a :class:`StringStream` instance
       replacing stderr.

    """

    def __init__(self, do_stdout=None, do_stderr=None):
        super(CaptureOutput, self).__init__()
        if do_stdout is None:
            self.do_stdout = (os.environ.get('OS_STDOUT_CAPTURE')
                              in _TRUE_VALUES)
        else:
            self.do_stdout = do_stdout
        if do_stderr is None:
            self.do_stderr = (os.environ.get('OS_STDERR_CAPTURE')
                              in _TRUE_VALUES)
        else:
            self.do_stderr = do_stderr
        self.stdout = None
        self.stderr = None

    def setUp(self):
        super(CaptureOutput, self).setUp()
        if self.do_stdout:
            self._stdout_fixture = fixtures.StringStream('stdout')
            self.stdout = self.useFixture(self._stdout_fixture).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        if self.do_stderr:
            self._stderr_fixture = fixtures.StringStream('stderr')
            self.stderr = self.useFixture(self._stderr_fixture).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', self.stderr))
