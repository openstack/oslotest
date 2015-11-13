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

from debtcollector import removals
import fixtures
from six.moves import mock


removals.removed_module("oslotest.mockpatch", replacement="fixtures",
                        version="1.13", removal_version="2.0",
                        message="Use fixtures.Mock* classes instead")


class _Base(fixtures.Fixture):
    def setUp(self):
        super(_Base, self).setUp()
        _p = self._get_p()
        self.addCleanup(_p.stop)
        self.mock = _p.start()


class PatchObject(_Base):
    """Deal with code around :func:`mock.patch.object`.

    .. py:attribute:: mock

        The mock as returned by :func:`mock.patch.object`.

    """

    def __init__(self, obj, attr, new=mock.DEFAULT, **kwargs):
        super(PatchObject, self).__init__()
        self._get_p = lambda: mock.patch.object(obj, attr, new, **kwargs)


class Patch(_Base):
    """Deal with code around :func:`mock.patch`.

    .. py:attribute:: mock

        The mock as returned by :func:`mock.patch`.

    """

    def __init__(self, obj, new=mock.DEFAULT, **kwargs):
        super(Patch, self).__init__()
        self._get_p = lambda: mock.patch(obj, new, **kwargs)


class Multiple(_Base):
    """Deal with code around :func:`mock.patch.multiple`.

    Pass name=value to replace obj.name with value.

    Pass name= :attr:`.DEFAULT` to replace obj.name with a
    :class:`mock.MagicMock` instance.

    :param obj: Object or name containing values being mocked.
    :type obj: str or object
    :param kwargs: names and values of attributes of obj to be mocked.

    .. py:attribute:: mock

        A :class:`dict`, where each key matches a kwarg parameter and the value
        is the passed-in value or :class:`mock.MagicMock`.

    """

    DEFAULT = mock.DEFAULT
    """Triggers a :class:`mock.MagicMock` to be created for the named
    attribute."""

    def __init__(self, obj, **kwargs):
        super(Multiple, self).__init__()
        self._get_p = lambda: mock.patch.multiple(obj, **kwargs)
