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


import ckanext.datarequests.constants as constants
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
    'organization_id': 'organization'
}


class AuthTest(unittest.TestCase):

    def setUp(self):
        self._tk = auth.tk
        auth.tk = MagicMock()

    def tearDown(self):
        auth.tk = self._tk

    @parameterized.expand([
        (auth.datarequest_create, None,    None),
        (auth.datarequest_create, context, None),
        (auth.datarequest_create, None,    request_data),
        (auth.datarequest_create, context, request_data),
        (auth.datarequest_show,   None,    None),
        (auth.datarequest_show,   context, None),
        (auth.datarequest_show,   None,    request_data),
        (auth.datarequest_show,   context, request_data),
        (auth.datarequest_index,  None,    None),
        (auth.datarequest_index,  context, None),
        (auth.datarequest_index,  None,    request_data),
        (auth.datarequest_index,  context, request_data),

    ])
    def test_everyone_can_create_and_show(self, function, context, request_data):
        self.assertTrue(function(context, request_data).get('success', False))

    @parameterized.expand([
        ('user_id', {'id': 'id', 'user_id': 'user_id'}, True, True),
        ('user_id', {'id': 'id', 'user_id': 'user_id'}, False, True),
        ('user_id', {'id': 'id', 'user_id': 'other_user_id'}, True, False),
        ('user_id', {'id': 'id', 'user_id': 'other_user_id'}, False, False),

    ])
    def test_datarequest_update(self, user_id, request_data, action_called, expected_result):

        user_obj = MagicMock()
        user_obj.id = user_id

        context = {'auth_user_obj': user_obj}

        if action_called:
            initial_request_data = {'id': request_data['id']}
            datarequest_show = auth.tk.get_action.return_value
            datarequest_show.return_value = request_data
        else:
            initial_request_data = request_data

        result = auth.datarequest_update(context, initial_request_data).get('success')
        self.assertEquals(expected_result, result)

        if action_called:
            auth.tk.get_action.assert_called_once_with(constants.DATAREQUEST_SHOW)
            datarequest_show = auth.tk.get_action.return_value
            datarequest_show.assert_called_once_with({'ignore_auth': True}, {'id': request_data['id']})
        else:
            self.assertEquals(0, auth.tk.get_action.call_count)




