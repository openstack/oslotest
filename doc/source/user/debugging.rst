===============
Debugging Tests
===============

Running tests through testrepository_ makes it difficult to use pdb for
debugging them. oslotest includes ``oslo_debug_helper`` to make using
pdb simpler/possible.

First, add a pdb call to the test code::

  import pdb; pdb.set_trace()

Then run the tests through ``oslo_debug_helper`` like

::

  $ oslo_debug_helper [tests to run]

or

::

  $ tox -e venv -- oslo_debug_helper [tests to run]

.. seealso::

   * https://wiki.openstack.org/wiki/Testr

.. _testrepository: https://pypi.org/project/testrepository
