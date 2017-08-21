# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from debtcollector import removals
import os_client_config


removals.removed_module("oslotest.functional",
                        version="2.9.0", removal_version="3.0",
                        message="oslotest.functional will be removed.")


def _get_openstack_auth(openstack_config, cloud_name, override_name):
    try:
        cloud_config = openstack_config.get_one_cloud(cloud_name)
    except os_client_config.exceptions.OpenStackConfigException:
        try:
            cloud_config = openstack_config.get_one_cloud(
                'devstack', auth=dict(
                    username=override_name, project_name=override_name))
        except os_client_config.exceptions.OpenStackConfigException:
            try:
                cloud_config = openstack_config.get_one_cloud('envvars')
            except os_client_config.exceptions.OpenStackConfigException:
                cloud_config = None
    return cloud_config


class FunctionalAuth(object):

    def __init__(self):
        # Collecting of credentials:
        #
        # Grab the cloud config from a user's clouds.yaml file.
        # First look for a functional_admin cloud, as this is a cloud
        # that the user may have defined for functional testing that has
        # admin credentials.
        #
        # If that is not found, get the devstack config and override the
        # username and project_name to be admin so that admin credentials
        # will be used.
        #
        # Finally, fall back to looking for environment variables to support
        # existing users running these the old way.
        openstack_config = os_client_config.config.OpenStackConfig()
        self._cloud_config = {}
        self._cloud_config['admin'] = _get_openstack_auth(
            openstack_config, 'functional_admin', 'admin')
        self._cloud_config['user'] = _get_openstack_auth(
            openstack_config, 'functional_user', 'demo')

    def get_auth_info(self, name):
        return self._cloud_config[name].config['auth']
