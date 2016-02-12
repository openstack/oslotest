# -*- coding: utf-8 -*-

# Copyright 2014 Deutsche Telekom AG
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

import os

import six

from oslotest import base
from oslotest import createfile


class CreateFileWithContentTest(base.BaseTestCase):

    def test_create_unicode_files(self):
        f = createfile.CreateFileWithContent(
            "no_approve",
            u'ಠ_ಠ',
        )
        f.setUp()
        with open(f.path, 'rb') as f:
            contents = f.read()
        self.assertEqual(u'ಠ_ಠ', six.text_type(contents, encoding='utf-8'))

    def test_create_unicode_files_encoding(self):
        f = createfile.CreateFileWithContent(
            "embarrassed", u'⊙﹏⊙', encoding='utf-8',
        )
        f.setUp()
        with open(f.path, 'rb') as f:
            contents = f.read()
        self.assertEqual(u'⊙﹏⊙', six.text_type(contents, encoding='utf-8'))

    def test_create_bad_encoding(self):
        f = createfile.CreateFileWithContent(
            "hrm", u'ಠ~ಠ', encoding='ascii',
        )
        self.assertRaises(UnicodeError, f.setUp)

    def test_prefix(self):
        f = createfile.CreateFileWithContent('testing', '')
        f.setUp()
        basename = os.path.basename(f.path)
        self.assertTrue(basename.startswith('testing'))

    def test_ext(self):
        f = createfile.CreateFileWithContent('testing', '', ext='.ending')
        f.setUp()
        basename = os.path.basename(f.path)
        self.assertTrue(basename.endswith('.ending'))
