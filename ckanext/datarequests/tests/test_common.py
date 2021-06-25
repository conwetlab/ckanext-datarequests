# -*- coding: utf-8 -*-

# Copyright (c) 2015 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of CKAN Data Requests Extension.

# CKAN Data Requests Extension is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CKAN Data Requests Extension is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with CKAN Data Requests Extension. If not, see <http://www.gnu.org/licenses/>.

from ckanext.datarequests import common
import unittest

from mock import patch


class DataRequestCommonTest(unittest.TestCase):

    def setUp(self):
        self.h_patch = patch('ckanext.datarequests.common.h')
        self.h_mock = self.h_patch.start()

    def tearDown(self):
        self.h_patch.stop()

    def test_is_fontawesome_4_false_ckan_version_does_not_exist(self):
        delattr(self.h_mock, 'ckan_version')
        self.assertFalse(common.is_fontawesome_4())

    def test_is_fontawesome_4_false_old_ckan_version(self):
        self.h_mock.ckan_version.return_value = '2.6.0'
        self.assertFalse(common.is_fontawesome_4())

    def test_is_fontawesome_4_true_new_ckan_version(self):
        self.h_mock.ckan_version.return_value = '2.7.0'
        self.assertTrue(common.is_fontawesome_4())

    def test_get_plus_icon_new(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.common.is_fontawesome_4', return_value=True)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('plus-square', common.get_plus_icon())

    def test_get_plus_icon_old(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.common.is_fontawesome_4', return_value=False)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('plus-sign-alt', common.get_plus_icon())

    def test_get_question_icon_new(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.common.is_fontawesome_4', return_value=True)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('question-circle', common.get_question_icon())

    def test_get_question_icon_old(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.common.is_fontawesome_4', return_value=False)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('question-sign', common.get_question_icon())
