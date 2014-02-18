==========
 oslotest
==========

OpenStack test framework and test fixtures

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/oslotest

Cross-testing With Other Projects
=================================

The oslotest package is cross-tested against its consuming projects to
ensure that no changes to the library break the tests in those other
projects.

In the Gate
-----------

To add your project to the list for cross-testing, update
``modules/openstack_project/files/jenkins_job_builder/config/projects.yaml``
in the openstack-infra/config git repository and add sections like:

::

   - '{pipeline}-oslo.test-dsvm-{name}{branch-designator}':
       pipeline: check
       node: 'devstack-precise || devstack-precise-check'
       branch-designator: ''
       branch-override: default
   - '{pipeline}-oslo.test-dsvm-{name}{branch-designator}':
       pipeline: gate
       node: devstack-precise
       branch-designator: ''
       branch-override: default

To the ``jobs`` list for your project. Refer to
https://review.openstack.org/#/c/76381 for an example.

Locally
-------

To run the cross-tests locally, invoke the script directly, passing
the path to the other source repository and the tox environment name
to use:

::

  $ cd oslo.test
  $ ./tools/run_cross_tests.sh ~/repos/openstack/oslo.config py27
