# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
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

"""Common utilities used in testing"""

import logging
import os
import tempfile

import fixtures
import six
from six.moves import mock
import testtools

_TRUE_VALUES = ('True', 'true', '1', 'yes')
_LOG_FORMAT = "%(levelname)8s [%(name)s] %(message)s"


class BaseTestCase(testtools.TestCase):
    """Base class for unit test classes.

    If the environment variable ``OS_TEST_TIMEOUT`` is set to an
    integer value, a timer is configured to control how long
    individual test cases can run. This lets tests fail for taking too
    long, and prevents deadlocks from completely hanging test runs.

    If the environment variable ``OS_STDOUT_CAPTURE`` is set, a fake
    stream replaces ``sys.stdout`` so the test can look at the output
    it produces.

    If the environment variable ``OS_STDERR_CAPTURE`` is set, a fake
    stream replaces ``sys.stderr`` so the test can look at the output
    it produces.

    If the environment variable ``OS_DEBUG`` is set to a true value,
    debug logging is enabled.

    If the environment variable ``OS_LOG_CAPTURE`` is set to a true
    value, a logging fixture is installed to capture the log output.

    Uses the fixtures_ module to configure a :class:`NestedTempFile`
    to ensure that all temporary files are created in an isolated
    location.

    Uses the fixtures_ module to configure a :class:`TempHomeDir` to
    change the ``HOME`` environment variable to point to a temporary
    location.

    PLEASE NOTE:
    Usage of this class may change the log level globally by setting the
    environment variable ``OS_DEBUG``. A mock of ``time.time`` will be called
    many more times than might be expected because it's called often by the
    logging module. A usage of such a mock should be avoided when a test needs
    to verify logging behavior or counts the number of invocations. A
    workaround is to overload the ``_fake_logs`` function in a base class but
    this will deactivate fake logging globally.

    .. _fixtures: https://pypi.python.org/pypi/fixtures

    """

    def __init__(self, *args, **kwds):
        super(BaseTestCase, self).__init__(*args, **kwds)
        # Ensure that the mock.patch.stopall cleanup is registered
        # before any setUp() methods have a chance to register other
        # things to be cleaned up, so it is called last. This allows
        # tests to register their own cleanups with a mock.stop method
        # so those mocks are not included in the stopall set.
        self.addCleanup(mock.patch.stopall)

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self._set_timeout()
        self._fake_output()
        self._fake_logs()
        self.useFixture(fixtures.NestedTempfile())
        self.useFixture(fixtures.TempHomeDir())

    def _set_timeout(self):
        test_timeout = os.environ.get('OS_TEST_TIMEOUT', 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            # If timeout value is invalid do not set a timeout.
            test_timeout = 0
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

    def _fake_output(self):
        if os.environ.get('OS_STDOUT_CAPTURE') in _TRUE_VALUES:
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if os.environ.get('OS_STDERR_CAPTURE') in _TRUE_VALUES:
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))

    def _fake_logs(self):
        level = None
        if os.environ.get('OS_DEBUG') in _TRUE_VALUES:
            level = logging.DEBUG
        capture_logs = os.environ.get('OS_LOG_CAPTURE') in _TRUE_VALUES
        if capture_logs:
            self.logger = self.useFixture(
                fixtures.FakeLogger(
                    format=_LOG_FORMAT,
                    level=level,
                    nuke_handlers=capture_logs,
                )
            )
        else:
            logging.basicConfig(format=_LOG_FORMAT, level=level)

    def create_tempfiles(self, files, ext='.conf', default_encoding='utf-8'):
        """Safely create temporary files.

        :param files: Sequence of tuples containing (filename, file_contents).
        :type files: list of tuple
        :param ext: File name extension for the temporary file.
        :type ext: str
        :param default_encoding: Default file content encoding when it is
                                 not provided, used to decode the tempfile
                                 contents from a text string into a binary
                                 string.
        :type default_encoding: str
        :return: A list of str with the names of the files created.
        """
        tempfiles = []
        for f in files:
            if len(f) == 3:
                basename, contents, encoding = f
            else:
                basename, contents = f
                encoding = default_encoding
            if isinstance(contents, six.text_type):
                contents = contents.encode(encoding)
            if not os.path.isabs(basename):
                (fd, path) = tempfile.mkstemp(prefix=basename, suffix=ext)
            else:
                path = basename + ext
                fd = os.open(path, os.O_CREAT | os.O_WRONLY)
            tempfiles.append(path)
            try:
                os.write(fd, contents)
            finally:
                os.close(fd)
        return tempfiles
