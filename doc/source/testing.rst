=======
Testing
=======

Cross-testing With Other Projects
=================================

The oslotest package can be cross-tested against its consuming
projects to ensure that no changes to the library break the tests in
those other projects.

In the Gate
-----------

Refer to the instructions in
https://wiki.openstack.org/wiki/Oslo/UsingALibrary for setting up
cross-test jobs in the gate.

Locally
-------

To run the cross-tests locally, invoke the script directly, passing
the path to the other source repository and the tox environment name
to use:

::

  $ cd oslo.test
  $ ./tools/oslo_run_cross_tests ~/repos/openstack/oslo.config py27

