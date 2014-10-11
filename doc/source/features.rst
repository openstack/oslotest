==========
 Features
==========

Debugging with oslo_debug_helper.sh
===================================

The oslotest package also distributes a shell file that may be used to assist
in debugging python code. The shell file uses testtools, and supports debugging
with `pdb <https://docs.python.org/2/library/pdb.html>`_.

Adding breakpoints to the code
------------------------------

The typical usage to break into the debugger from a running program is to
insert:

.. code-block:: python

  import pdb; pdb.set_trace()

Update tox.ini
--------------

Within the ``tox.ini`` file of your project add the following::

  [testenv:debug]
  commands = oslo_debug_helper {posargs}

If the project name, and the module that precedes the tests directory do not
match, then consider passing an argument to ``tox.ini``.

For example, ``python-keystoneclient`` project has tests in
``keystoneclient/tests``, thus it would have to pass in::

  [testenv:debug]
  commands = oslo_debug_helper -t keystoneclient/tests {posargs}

Similarily, most ``oslo`` projects have the tests at the package level, it
would have to pass in::

  [testenv:debug]
  commands = oslo_debug_helper -t tests {posargs}

To run with tox:

.. code-block:: bash

  $ tox -e debug
  $ tox -e debug test_notifications
  $ tox -e debug test_notifications.NotificationsTestCase
  $ tox -e debug test_notifications.NotificationsTestCase.test_send_notification
