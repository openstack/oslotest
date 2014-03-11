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

to the ``jobs`` list for your project. Refer to
https://review.openstack.org/#/c/76381 for an example.

Then update ``modules/openstack_project/files/zuul/layout.yaml`` by
adding the new check test to the global list of jobs (to make it
non-voting to start), and then to your project and to oslo.test.

::

  - name: check-oslo.test-dsvm-oslo.messaging
    voting: false

::

    - name: openstack/oslo.messaging
      ...
      check:
      ...
        - check-oslo.test-dsvm-oslo.messaging
      ...

::

    - name: openstack/oslo.test
      ...
      check:
      ...
        - check-oslo.test-dsvm-oslo.messaging
      ...


Locally
-------

To run the cross-tests locally, invoke the script directly, passing
the path to the other source repository and the tox environment name
to use:

::

  $ cd oslo.test
  $ ./tools/run_cross_tests.sh ~/repos/openstack/oslo.config py27
