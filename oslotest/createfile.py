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
import tempfile

import fixtures
import six


class CreateFileWithContent(fixtures.Fixture):
    """Create a temporary file with the given content.

    Creates a file using a predictable name, to be used by tests for
    code that need a filename to load data or otherwise interact with
    the real filesystem.

    .. warning::

       It is the responsibility of the caller to ensure that the file
       is removed.

    Users of this fixture may also want to use
    :class:`fixtures.NestedTempfile` to set the temporary directory
    somewhere safe and to ensure the files are cleaned up.

    .. py:attribute:: path

       The canonical name of the file created.

    :param filename: Base file name or full literal path to the file
        to be created.
    :param contents: The data to write to the file. Unicode data will
        be encoded before being written.
    :param ext: An extension to add to filename.
    :param encoding: An encoding to use for unicode data (ignored for
        byte strings).

    """

    def __init__(self, filename, contents, ext='.conf', encoding='utf-8'):
        self._filename = filename
        self._contents = contents
        self._ext = ext
        self._encoding = encoding

    def setUp(self):
        super(CreateFileWithContent, self).setUp()
        contents = self._contents
        if isinstance(contents, six.text_type):
            contents = contents.encode(self._encoding)
        if not os.path.isabs(self._filename):
            (fd, self.path) = tempfile.mkstemp(prefix=self._filename,
                                               suffix=self._ext)
        else:
            self.path = self._filename + self._ext
            fd = os.open(self.path, os.O_CREAT | os.O_WRONLY)
        try:
            os.write(fd, contents)
        finally:
            os.close(fd)
