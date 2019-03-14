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

request_data_dr = {
    'title': 'title',
    'description': 'description',
    'organization_id': 'organization'
}

request_data_comment = {
    'id': 'title',
    'datarequest_id': 'example_uuid_v4',
    'comment': 'This is an example comment'
}

request_follow = {
    'datarequest_id': 'example_uuid_v4',
}


class AuthTest(unittest.TestCase):

    def setUp(self):
        self._tk = auth.tk
        auth.tk = MagicMock()

    def tearDown(self):
        auth.tk = self._tk

    @parameterized.expand([
        # Data Requests
        (auth.create_datarequest, None,    None),
        (auth.create_datarequest, context, None),
        (auth.create_datarequest, None,    request_data_dr),
        (auth.create_datarequest, context, request_data_dr),
        (auth.show_datarequest,   None,    None),
        (auth.show_datarequest,   context, None),
        (auth.show_datarequest,   None,    request_data_dr),
        (auth.show_datarequest,   context, request_data_dr),
        (auth.list_datarequests,  None,    None),
        (auth.list_datarequests,  context, None),
        (auth.list_datarequests,  None,    request_data_dr),
        (auth.list_datarequests,  context, request_data_dr),
        # Comments
        (auth.comment_datarequest,        None,    None),
        (auth.comment_datarequest,        context, None),
        (auth.comment_datarequest,        None,    request_data_comment),
        (auth.comment_datarequest,        context, request_data_comment),
        (auth.show_datarequest_comment,   None,    None),
        (auth.show_datarequest_comment,   context, None),
        (auth.show_datarequest_comment,   None,    request_data_comment),
        (auth.show_datarequest_comment,   context, request_data_comment),
        (auth.list_datarequest_comments,  None,    request_data_comment),
        (auth.list_datarequest_comments,  context, request_data_comment),
        # Follow/Unfollow
        (auth.follow_datarequest,   None,    None),
        (auth.follow_datarequest,   context, None),
        (auth.follow_datarequest,   None,    request_follow),
        (auth.follow_datarequest,   context, request_follow),
        (auth.unfollow_datarequest, None,    None),
        (auth.unfollow_datarequest, context, None),
        (auth.unfollow_datarequest, None,    request_follow),
        (auth.unfollow_datarequest, context, request_follow),
    ])
    def test_everyone_can_create_show_and_index(self, function, context, request_data):
        self.assertTrue(function(context, request_data).get('success', False))

    @parameterized.expand([
        # Data Requests
        (auth.update_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, True, True),
        (auth.update_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, False, True),
        (auth.update_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, True, False),
        (auth.update_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, False, False),
        (auth.delete_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, True, True),
        (auth.delete_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, False, True),
        (auth.delete_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, True, False),
        (auth.delete_datarequest, constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, False, False),
        (auth.close_datarequest,  constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, True, True),
        (auth.close_datarequest,  constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, False, True),
        (auth.close_datarequest,  constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, True, False),
        (auth.close_datarequest,  constants.SHOW_DATAREQUEST,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, False, False),
        # Comments
        (auth.update_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, True, True),
        (auth.update_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, False, True),
        (auth.update_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, True, False),
        (auth.update_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, False, False),
        (auth.delete_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, True, True),
        (auth.delete_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'user_id'}, False, True),
        (auth.delete_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, True, False),
        (auth.delete_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT,
            'user_id', {'id': 'id', 'user_id': 'other_user_id'}, False, False),

    ])
    def test_update_delete_datarequest(self, function, show_function, user_id, request_data, action_called, expected_result):

        user_obj = MagicMock()
        user_obj.id = user_id

        context = {'auth_user_obj': user_obj}

        if action_called:
            initial_request_data = {'id': request_data['id']}
            xyz_show = auth.tk.get_action.return_value
            xyz_show.return_value = request_data
        else:
            initial_request_data = request_data

        result = function(context, initial_request_data).get('success')
        self.assertEquals(expected_result, result)

        if action_called:
            auth.tk.get_action.assert_called_once_with(show_function)
            xyz_show = auth.tk.get_action.return_value
            xyz_show.assert_called_once_with({'ignore_auth': True}, {'id': request_data['id']})
        else:
            self.assertEquals(0, auth.tk.get_action.call_count)
