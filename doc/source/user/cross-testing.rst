==========================
Cross-project Unit Testing
==========================

Libraries in OpenStack have an unusual ability to introduce breaking
changes. All of the projects are run together from source in one form
or another during the integration tests, but they are not combined
from source when unit tests are run. The server applications do not
generally import code from other projects, so their unit tests are
isolated. The libraries, however, are fundamentally intended to be
used during unit tests as well as integration tests. Testing the full
cross-product of libraries and consuming projects would consume all
available test servers, and so we cannot run all of the tests on all
patches to the libraries. As an alternative, we have a few scripts in
``oslotest`` for running the unit tests in serial. The result takes
far too long (usually overnight) to run in the OpenStack
infrastructure. Instead, they are usually run by hand on a dedicated
system. A cloud VM works well for this purpose, especially considering
how much of it is now automated.

Check Out OpenStack Source
==========================

The first step for all of the cross-project unit tests tools is to
ensure that you have a full copy of the OpenStack source checked
out. You can do this yourself through gerrit's ssh API, or you can use
the ``clone_openstack.sh`` command in the tools directory of the
``openstack/oslo-incubator`` repository.

For example::

  $ mkdir -p ~/repos/openstack
  $ cd ~/repos/openstack
  $ git clone https://opendev.org/openstack/oslo-incubator
  $ cd ~/repos
  $ ./openstack/oslo-incubator/tools/clone_openstack.sh

The first time the script runs it will take quite some time, since it
has to download the entire history of every OpenStack project.

Testing One Project
===================

``oslo_run_cross_tests`` runs one set of unit tests for one library
against all of the consuming projects. It should be run from the
directory with the library to be tested, and passed arguments telling
it about another project whose tests should be run.

For example, to run the ``py27`` test suite from nova using the
currently checked out sources for ``oslo.config``, run::

  $ cd ~/repos/openstack/oslo.config
  $ tox -e venv -- oslo_run_cross_tests ~/repos/openstack/nova py27

Testing All Consumers
=====================

``oslo_run_pre_release_tests`` builds on ``oslo_run_cross_tests`` to
find all of the consuming projects and run their tests
automatically. The pre-release script needs to know where the source
has been checked out, so the first step is to create its configuration
file.

Edit ``~/.oslo.conf`` to contain::

  [DEFAULT]
  repo_root = /path/to/repos

Replace ``/path/to/repos`` with the full, expanded, absolute path to
the location where the source code was checked out. For example, if
you followed the instructions above using ``clone_openstack.sh`` in
``~/repos`` and your user name is ``theuser`` the path would be
``/home/theuser/repos``.

Returning to the earlier example, to test ``oslo.config`` with all of
the projects that use it, go to the ``oslo.config`` source directory
and run ``oslo_run_pre_release_tests``.

::

  $ cd ~/repos/openstack/oslo.config
  $ tox -e venv -- oslo_run_pre_release_tests

The output for each test set is logged to a separate file in the
current directory, to make them easy to examine.

Use the ``--update`` or ``-u`` option to force a ``git pull`` for each
consuming projects before running its tests (useful for maintaining a
long-running system to host these tests).

Use the ``--verbose`` or ``-v`` option to report more verbosely about
what is happening, including the number of projects being tested.

Use ``--env`` or ``-e`` to add a tox environment to test. By default
the ``py27`` and ``pep8`` environments are used because those have
been shown to provide a good balance between finding problems and
running the tests quickly.

Use the ``--ref`` option to test a specific commit reference of the
library under test. The default is to leave the source directory
untouched, but if this option is specified ``git checkout`` is used to
force the source tree to the specified reference.
