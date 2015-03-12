# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

import fixtures
from six.moves import mock


class _Base(fixtures.Fixture):
    def setUp(self):
        super(_Base, self).setUp()
        _p = self._get_p()
        self.addCleanup(_p.stop)
        self.mock = _p.start()


class PatchObject(_Base):
    """Deal with code around mock."""

    def __init__(self, obj, attr, new=mock.DEFAULT, **kwargs):
        super(PatchObject, self).__init__()
        self._get_p = lambda: mock.patch.object(obj, attr, new, **kwargs)


class Patch(_Base):
    """Deal with code around mock.patch."""

    def __init__(self, obj, new=mock.DEFAULT, **kwargs):
        super(Patch, self).__init__()
        self._get_p = lambda: mock.patch(obj, new, **kwargs)


class Multiple(_Base):
    """Deal with code around mock.patch.multiple."""

    # Default value to trigger a MagicMock to be created for a named
    # attribute.
    DEFAULT = mock.DEFAULT

    def __init__(self, obj, **kwargs):
        """Initialize the mocks

        Pass name=value to replace obj.name with value.

        Pass name=Multiple.DEFAULT to replace obj.name with a
        MagicMock instance.

        :param obj: Object or name containing values being mocked.
        :type obj: str or object
        :param kwargs: names and values of attributes of obj to be mocked.

        """
        super(Multiple, self).__init__()
        self._get_p = lambda: mock.patch.multiple(obj, **kwargs)
