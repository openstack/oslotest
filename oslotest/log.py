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

import logging
import os

import fixtures

_TRUE_VALUES = ('True', 'true', '1', 'yes')


class ConfigureLogging(fixtures.Fixture):
    """Configure logging.

    The behavior is managed through two environment variables. If
    ``OS_DEBUG`` is true then the logging level is set to debug. If
    ``OS_LOG_CAPTURE`` is true a FakeLogger is configured.

    "True" values include ``True``, ``true``, ``1``, and ``yes``.

    .. py:attribute:: logger

       The logger fixture, if it is created.

    .. py:attribute:: level

       ``logging.DEBUG`` if debug logging is enabled, otherwise
       ``None``.

    :param format: The logging format string to use.

    """

    DEFAULT_FORMAT = "%(levelname)8s [%(name)s] %(message)s"
    """Default log format"""

    def __init__(self, format=DEFAULT_FORMAT):
        super(ConfigureLogging, self).__init__()
        self._format = format
        self.level = None
        if os.environ.get('OS_DEBUG') in _TRUE_VALUES:
            self.level = logging.DEBUG
        self.capture_logs = os.environ.get('OS_LOG_CAPTURE') in _TRUE_VALUES
        self.logger = None

    def setUp(self):
        super(ConfigureLogging, self).setUp()
        if self.capture_logs:
            self.logger = self.useFixture(
                fixtures.FakeLogger(
                    format=self._format,
                    level=self.level,
                    nuke_handlers=True,
                )
            )
        else:
            logging.basicConfig(format=self._format, level=self.level)
