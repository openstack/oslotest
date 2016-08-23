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

import sys

import fixtures


class DisableModuleFixture(fixtures.Fixture):
    """A fixture to provide support for unloading/disabling modules."""

    def __init__(self, module, *args, **kwargs):
        super(DisableModuleFixture, self).__init__(*args, **kwargs)
        self.module = module

    def setUp(self):
        """Ensure ImportError for the specified module."""
        super(DisableModuleFixture, self).setUp()

        cleared_modules = {}

        for name in list(sys.modules.keys()):
            if name == self.module or name.startswith(self.module + '.'):
                cleared_modules[name] = sys.modules.pop(name)

        finder = _NoModuleFinder(self.module)
        sys.meta_path.insert(0, finder)

        self.addCleanup(sys.meta_path.remove, finder)
        self.addCleanup(sys.modules.update, cleared_modules)


class _NoModuleFinder(object):
    """Disallow further imports of 'module'."""

    def __init__(self, module):
        self.module = module

    def find_module(self, fullname, path):
        if fullname == self.module or fullname.startswith(self.module + '.'):
            raise ImportError
