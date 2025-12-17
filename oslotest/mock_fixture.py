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

from __future__ import annotations

from collections.abc import Callable
import functools
from typing import Any, TypeVar, TYPE_CHECKING
from unittest import mock

import fixtures

_F = TypeVar('_F', bound=Callable[..., Any])
_T = TypeVar('_T')


def _lazy_autospec_method(
    mocked_method: Any,
    original_method: Any,
    eat_self: bool,
) -> None:
    if mocked_method._mock_check_sig.__dict__.get('autospeced'):
        return

    _lazy_autospec: Any = mock.create_autospec(original_method)
    if eat_self:
        # consume self argument.
        _lazy_autospec = functools.partial(_lazy_autospec, None)

    def _autospeced(*args: Any, **kwargs: Any) -> None:
        _lazy_autospec(*args, **kwargs)

    # _mock_check_sig is called by the mock's __call__ method.
    # which means that if a method is not called, _autospeced is not
    # called.
    _autospeced.__dict__['autospeced'] = True
    mocked_method._mock_check_sig = _autospeced


class _AutospecMockMixin:
    """Mock object that lazily autospecs the given spec's methods."""

    # These are defined by mock.Mock but we need to declare them for typing
    return_value: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
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

    def __getattr__(self, name: str) -> Any:
        attr = super().__getattr__(name)  # type: ignore[misc]

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
            # NOTE: _must_skip is a private function in the mock module
            eat_self = mock._must_skip(  # type: ignore[attr-defined]
                original_spec, name, isinstance(original_spec, type)
            )

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

    def setUp(self) -> None:
        super().setUp()

        # patch both external and internal usage of Mock / MagicMock.
        self.useFixture(
            fixtures.MonkeyPatch('unittest.mock.Mock', _AutospecMock)
        )
        self.useFixture(
            fixtures.MonkeyPatch('unittest.mock.MagicMock', _AutospecMagicMock)
        )


if TYPE_CHECKING:
    Base = mock._patch
else:
    # as of Python 3.13 this is not subscriptable at runtime
    class Base(mock._patch):
        def __class_getitem__(cls, _):
            return cls


class _patch(Base[_T]):
    """Patch class with working autospec functionality.

    Currently, mock.patch functionality doesn't handle the autospec parameter
    properly (the self argument is not consumed, causing assertions to fail).
    Until the issue is addressed in the mock library, this should be used
    instead.
    https://github.com/testing-cabal/mock/issues/396
    """

    def __enter__(self) -> _T:
        # NOTE(claudiub): we're doing the autospec checks here so unit tests
        # have a chance to set up mocks in advance (e.g.: mocking platform
        # specific libraries, which would cause the patch to fail otherwise).

        # By default, autospec is None. We will consider it as True.
        autospec = True if self.autospec is None else self.autospec

        # in some cases, autospec cannot be set to True.
        skip_autospec = (
            getattr(self, attr) for attr in ['new_callable', 'create', 'spec']
        )
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
            # NOTE: _must_skip is a private function in the mock module
            eat_self = mock._must_skip(  # type: ignore[attr-defined]
                target, self.attribute, isinstance(target, type)
            )

            new = super().__enter__()

            # NOTE(claudiub): mock.patch.multiple will cause new to be a
            # dict.
            mocked_method = (
                new[self.attribute] if isinstance(new, dict) else new
            )
            _lazy_autospec_method(mocked_method, original_attr, eat_self)
            return new
        else:
            return super().__enter__()


def _safe_attribute_error_wrapper(func: _F) -> _F:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except AttributeError:
            pass

    return wrapper  # type: ignore[return-value]


def patch_mock_module() -> None:
    """Replaces the mock.patch class."""
    # NOTE: _patch is a private class in the mock module
    mock._patch = _patch  # type: ignore[misc]

    # NOTE(claudiub): mock cannot autospec partial functions properly,
    # especially those created by LazyLoader objects (scheduler client),
    # as it will try to copy the partial function's __name__ (which they do
    # not have).
    # NOTE: _copy_func_details is a private function in the mock module
    mock._copy_func_details = _safe_attribute_error_wrapper(  # type: ignore[attr-defined]
        mock._copy_func_details  # type: ignore[attr-defined]
    )
