
# Copyright 2017 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools

import fixtures
import mock


def _lazy_autospec_method(mocked_method, original_method, eat_self):
    if mocked_method._mock_check_sig.__dict__.get('autospeced'):
        return

    _lazy_autospec = mock.create_autospec(original_method)
    if eat_self:
        # consume self argument.
        _lazy_autospec = functools.partial(_lazy_autospec, None)

    def _autospeced(*args, **kwargs):
        _lazy_autospec(*args, **kwargs)

    # _mock_check_sig is called by the mock's __call__ method.
    # which means that if a method is not called, _autospeced is not
    # called.
    _autospeced.__dict__['autospeced'] = True
    mocked_method._mock_check_sig = _autospeced


class _AutospecMockMixin(object):
    """Mock object that lazily autospecs the given spec's methods."""

    def __init__(self, *args, **kwargs):
        super(_AutospecMockMixin, self).__init__(*args, **kwargs)
        autospec = kwargs.get('autospec')
        self.__dict__['_autospec'] = autospec
        _mock_methods = self.__dict__['_mock_methods']
        if _mock_methods:
            # this will allow us to be able to set _mock_check_sig if
            # the spec_set argument has been given.
            _mock_methods.append('_mock_check_sig')

        # callable mocks with autospecs (e.g.: the given autospec is a class)
        # should have their return values autospeced as well.
        if autospec:
            self.return_value.__dict__['_autospec'] = autospec

    def __getattr__(self, name):
        attr = super(_AutospecMockMixin, self).__getattr__(name)

        original_spec = self.__dict__['_autospec']
        if not original_spec:
            return attr

        if not hasattr(original_spec, name):
            raise AttributeError(name)

        # check if the original attribute is callable, and the mock was not
        # autospeced already.
        original_attr = getattr(original_spec, name)
        if callable(original_attr):
            # lazily autospec callable attribute.
            eat_self = mock.mock._must_skip(original_spec, name,
                                            isinstance(original_spec, type))

            _lazy_autospec_method(attr, original_attr, eat_self)

        return attr


class _AutospecMock(_AutospecMockMixin, mock.Mock):
    pass


class _AutospecMagicMock(_AutospecMockMixin, mock.MagicMock):
    pass


class MockAutospecFixture(fixtures.Fixture):
    """A fixture to add / fix the autospec feature into the mock library.

    The current version of the mock library has a few unaddressed issues, which
    can lead to erroneous unit tests, and can hide actual issues. This fixture
    is to be removed once these issues have been addressed in the mock library.

    Issue addressed by the fixture:

    * mocked method's signature checking:
        - https://github.com/testing-cabal/mock/issues/393
        - mock can only accept a spec object / class, and it makes sure that
          that attribute exists, but it does not check whether the given
          attribute is callable, or if its signature is respected in any way.
        - adds autospec argument. If the autospec argument is given, the
          mocked method's signature is also checked.
    """

    def setUp(self):
        super(MockAutospecFixture, self).setUp()

        # patch both external and internal usage of Mock / MagicMock.
        self.useFixture(fixtures.MonkeyPatch('mock.Mock', _AutospecMock))
        self.useFixture(fixtures.MonkeyPatch('mock.mock.Mock', _AutospecMock))
        self.useFixture(fixtures.MonkeyPatch('mock.MagicMock',
                                             _AutospecMagicMock))
        self.useFixture(fixtures.MonkeyPatch('mock.mock.MagicMock',
                                             _AutospecMagicMock))


class _patch(mock.mock._patch):
    """Patch class with working autospec functionality.

    Currently, mock.patch functionality doesn't handle the autospec parameter
    properly (the self argument is not consumed, causing assertions to fail).
    Until the issue is addressed in the mock library, this should be used
    instead.
    https://github.com/testing-cabal/mock/issues/396
    """

    def __enter__(self):
        # NOTE(claudiub): we're doing the autospec checks here so unit tests
        # have a chance to set up mocks in advance (e.g.: mocking platform
        # specific libraries, which would cause the patch to fail otherwise).

        # By default, autospec is None. We will consider it as True.
        autospec = True if self.autospec is None else self.autospec

        # in some cases, autospec cannot be set to True.
        skip_autospec = (getattr(self, attr) for attr in
                         ['new_callable', 'create', 'spec'])
        # NOTE(claudiub): The "new" argument is always mock.DEFAULT, unless
        # explicitly set otherwise.
        if self.new is not mock.DEFAULT or any(skip_autospec):
            # cannot autospec if new, new_callable, or create arguments given.
            autospec = False
        elif self.attribute:
            target = getattr(self.getter(), self.attribute, None)
            if isinstance(target, mock.Mock):
                # NOTE(claudiub): shouldn't autospec already mocked targets.
                # this can cause some issues. There are quite a few tests
                # which patch mocked methods.
                autospec = False

        # NOTE(claudiub): reset the self.autospec property, so we can handle
        # the autospec scenario ourselves.
        self.autospec = None

        if autospec:
            target = self.getter()
            original_attr = getattr(target, self.attribute)
            eat_self = mock.mock._must_skip(target, self.attribute,
                                            isinstance(target, type))

            new = super(_patch, self).__enter__()

            # NOTE(claudiub): mock.patch.multiple will cause new to be a
            # dict.
            mocked_method = (new[self.attribute] if isinstance(new, dict)
                             else new)
            _lazy_autospec_method(mocked_method, original_attr, eat_self)
            return new
        else:
            return super(_patch, self).__enter__()


def _safe_attribute_error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError:
            pass

    return wrapper


def patch_mock_module():
    """Replaces the mock.patch class."""
    mock.mock._patch = _patch

    # NOTE(claudiub): mock cannot autospec partial functions properly,
    # especially those created by LazyLoader objects (scheduler client),
    # as it will try to copy the partial function's __name__ (which they do
    # not have).
    mock.mock._copy_func_details = _safe_attribute_error_wrapper(
        mock.mock._copy_func_details)
