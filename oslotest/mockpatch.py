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
"""Deprecated.

This module is deprecated since version 1.13 and may be removed in version 2.0.
Use fixtures.Mock* classes instead.

"""

from debtcollector import removals
import fixtures


removals.removed_module("oslotest.mockpatch", replacement="fixtures",
                        version="1.13", removal_version="2.0",
                        message="Use fixtures.Mock* classes instead.")


PatchObject = fixtures.MockPatchObject
Patch = fixtures.MockPatch
Multiple = fixtures.MockPatchMultiple
