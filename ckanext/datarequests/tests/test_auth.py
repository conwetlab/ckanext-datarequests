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


import ckanext.datarequests.auth as auth
import unittest

from mock import MagicMock
from nose_parameterized import parameterized

# Needed for the test
context = {
    'user': 'example_usr',
    'auth_user_obj': MagicMock(),
    'model': MagicMock(),
    'session': MagicMock()
}

request_data = {
    'title': 'title',
    'description': 'description',
    'organization': 'organization'
}


class AuthTest(unittest.TestCase):

    @parameterized.expand([
        (None,    None),
        (context, None),
        (None,    request_data),
        (context, request_data)
    ])
    def test_datarequest_create_is_true(self, context, request_data):
        self.assertTrue(auth.datarequest_create(context, request_data))
