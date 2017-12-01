=============
Mock autospec
=============

In typical unit tests, almost all of the dependencies are mocked or patched
(``mock.patch``), without any guarantee that the mocked methods actually exist,
or if their signatures are respected. Because of this, actual issues can be
easily overlooked and missed, as the unit tests are wrongfully passing.

The ``mock.Mock`` class accepts a spec as an argument, which only solves half
the problem: it only checks if an attribute exists, based on the given spec. It
does not guarantee that the given attribute is actually a method, or if its
signature is respected. The Mock class does not accept an autospec argument [1].

``mock.patch``, ``mock.patch.object``, ``mock.patch.multiple`` accept an
autospec argument, but because of a bug [2], it cannot be used properly.

oslotest offers a solution for problems mentioned above.

1. https://github.com/testing-cabal/mock/issues/393
2. https://github.com/testing-cabal/mock/issues/396


Patching the ``mock`` module
============================

The ``oslotest.mock_fixture`` module contains 2 components:

- patch_mock_module
- MockAutospecFixture

Both components need to be used in order to fix various issues within ``mock``
regarding autospec.

patch_mock_module
-----------------

At the moment, ``mock.patch``, ``mock.patch.object``, ``mock.patch.multiple``
accepts the ``autospec`` argument, but it does not correctly consume the
self / cls argument of methods or class methods.

``patch_mock_module`` addresses this issue. In order to make sure that the
original version of ``mock.patch`` is not used by the unit tests, this
function has to be called as early as possible within the test module, or
the base test module. E.g.::

    nova/test.py
    ...
    from oslotest import mock_fixture

    mock_fixture.patch_mock_module()

Additionally, this function will set the ``autospec`` argument's value
to ``True``, unless otherwise specified or these arguments are passed in:
``new_callable, create, spec``.

MockAutospecFixture
-------------------

``mock.Mock`` and ``mock.MagicMock`` classes do not accept any ``autospec``
argument. This fixture will replace the ``mock.Mock`` and ``mock.MagicMock``
classes with subclasses which accepts the said argument.

The fixture can be used in the test ``setUp`` method. E.g.::

    nova/test.py
    ...
    from oslotest import mock_fixture

    class TestCase(testtools.TestCase):
        def setUp(self):
            super(TestCase, self).setUp()
            self.useFixture(mock_fixture.MockAutospecFixture())


Mock autospec usage
===================

Consider the following class as an example::

    class Foo(object):
        def bar(self, a, b, c, d=None):
            pass

Using the setup described above, the following unit tests will now pass
correctly::

    class FooTestCase(TestCase):
        def test_mock_bar(self):
            mock_foo = mock.Mock(autospec=Foo)
            self.assertRaises(TypeError, mock_foo.bar, invalid='argument')

        @mock.patch.object(Foo, 'bar', autospec=True)
        def test_patch_bar(self, mock_bar):
            foo = Foo()
            self.assertRaises(TypeError, foo.bar, invalid='argument')
