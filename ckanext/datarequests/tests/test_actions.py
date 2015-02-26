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

import ckanext.datarequests.actions as actions
import ckanext.datarequests.constants as constants
import datetime
import test_actions_data as test_data
import unittest

from mock import MagicMock
from nose_parameterized import parameterized


class ActionsTest(unittest.TestCase):

    def setUp(self):
        # Mocks
        self._tk = actions.tk
        actions.tk = MagicMock()
        actions.tk.ObjectNotFound = self._tk.ObjectNotFound
        actions.tk.ValidationError = self._tk.ValidationError

        self._c = actions.c
        actions.c = MagicMock()

        self._db = actions.db
        actions.db = MagicMock()

        self._validator = actions.validator
        actions.validator = MagicMock()

        self._datetime = actions.datetime
        actions.datetime = MagicMock()

        self.context = {
            'user': 'example_usr',
            'auth_user_obj': MagicMock(),
            'model': MagicMock(),
            'session': MagicMock()
        }

    def tearDown(self):
        # Unmock
        actions.tk = self._tk
        actions.c = self._c
        actions.db = self._db
        actions.validator = self._validator
        actions.datetime = self._datetime

    def _check_basic_response(self, datarequest, response):
        self.assertEquals(datarequest.id, response['id'])
        self.assertEquals(datarequest.user_id, response['user_id'])
        self.assertEquals(datarequest.title, response['title'])
        self.assertEquals(datarequest.description, response['description'])
        self.assertEquals(datarequest.organization_id, response['organization_id'])
        self.assertEquals(str(datarequest.open_time), response['open_time'])
        self.assertEquals(datarequest.closed, response['closed'])
        self.assertEquals(datarequest.accepted_dataset, response['accepted_dataset'])

        if datarequest.close_time:
            self.assertEquals(str(datarequest.close_time), response['close_time'])
        else:
            self.assertIsNone(response['close_time'])

    def _test_not_authorized(self, function, action, request_data):
        # Configure the mock
        actions.tk.check_access = MagicMock(side_effect=self._tk.NotAuthorized)

        # Call the function
        with self.assertRaises(self._tk.NotAuthorized):
            function(self.context, request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(action, self.context, request_data)
        self.assertEquals(0, actions.db.DataRequest.get.call_count)

    def _test_not_found(self, function, action, request_data):
        # Configure the mock
        actions.db.DataRequest.get.return_value = []

        # Call the function
        with self.assertRaises(self._tk.ObjectNotFound):
            function(self.context, request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(action, self.context, request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=test_data.show_request_data['id'])

    def _test_no_id(self, function):
        # Call the function
        with self.assertRaises(self._tk.ValidationError):
            function(self.context, {})

        # Assertions
        self.assertEquals(0, actions.db.init_db.call_count)
        self.assertEquals(0, actions.tk.check_access.call_count)
        self.assertEquals(0, actions.db.DataRequest.get.call_count)

    def test_datarequest_create_no_access(self):
        # Configure the mock
        actions.tk.check_access = MagicMock(side_effect=self._tk.NotAuthorized)

        # Call the function
        with self.assertRaises(self._tk.NotAuthorized):
            actions.datarequest_create(self.context, test_data.create_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, self.context, test_data.create_request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_datarequest_create_invalid(self):
        # Configure the mock
        actions.validator.validate_datarequest = MagicMock(side_effect=self._tk.ValidationError({'error': 'MSG ERROR'}))

        # Call the function
        with self.assertRaises(self._tk.ValidationError):
            actions.datarequest_create(self.context, test_data.create_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, self.context, test_data.create_request_data)
        actions.validator.validate_datarequest.assert_called_once_with(self.context, test_data.create_request_data)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_datarequest_create_valid(self):
        # Configure the mocks
        current_time = self._datetime.datetime.now()
        actions.datetime.datetime.now = MagicMock(return_value=current_time)

        # Call the function
        result = actions.datarequest_create(self.context, test_data.create_request_data)
        
        # Assertions
        datarequest = actions.db.DataRequest.return_value

        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, self.context, test_data.create_request_data)
        actions.validator.validate_datarequest.assert_called_once_with(self.context, test_data.create_request_data)
        actions.db.DataRequest.assert_called_once()

        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once()

        self.assertEquals(self.context['auth_user_obj'].id, datarequest.user_id)
        self.assertEquals(test_data.create_request_data['title'], datarequest.title)
        self.assertEquals(test_data.create_request_data['description'], datarequest.description)
        self.assertEquals(test_data.create_request_data['organization_id'], datarequest.organization_id)
        self.assertEquals(current_time, datarequest.open_time)

        self._check_basic_response(datarequest, result)

    def test_datarequest_show_not_authorized(self):
        self._test_not_authorized(actions.datarequest_show, constants.DATAREQUEST_SHOW, test_data.show_request_data)

    def test_datarequest_show_not_found(self):
        self._test_not_found(actions.datarequest_show, constants.DATAREQUEST_SHOW, test_data.show_request_data)

    def test_datarequest_show_no_id(self):
        self._test_no_id(actions.datarequest_show)

    def _test_datarequest_show_found(self, datarequest):
        # Configure mock
        actions.db.DataRequest.get.return_value = [datarequest]

        # Call the function
        result = actions.datarequest_show(self.context, test_data.show_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_SHOW, self.context, test_data.show_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=test_data.show_request_data['id'])

        self._check_basic_response(datarequest, result)
        self.assertEquals(datarequest.accepted_dataset, result['accepted_dataset'])
        expected_close_time = str(datarequest.close_time) if datarequest.close_time else None
        self.assertEquals(expected_close_time, result['close_time'])
        self.assertEquals(datarequest.closed, result['closed'])

    def test_datarequest_show_found_open(self):
        datarequest = test_data._generate_basic_datarequest()
        self._test_datarequest_show_found(datarequest)

    def test_datarequest_show_found_closed(self):
        datarequest = test_data._generate_basic_datarequest()
        datarequest.accepted_dataset = 'example_uuidv4_package'
        datarequest.close_time = datetime.datetime.now()
        datarequest.closed = True

        self._test_datarequest_show_found(datarequest)

    def test_datarequest_update_not_authorized(self):
        self._test_not_authorized(actions.datarequest_update, constants.DATAREQUEST_UPDATE, test_data.update_request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_datarequest_update_no_id(self):
        self._test_no_id(actions.datarequest_update)

    def test_datarequest_update_not_found(self):
        self._test_not_found(actions.datarequest_update, constants.DATAREQUEST_UPDATE, test_data.update_request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    @parameterized.expand([
        (True,),
        (False,)
    ])
    def test_datarequest_update(self, title_checked):
        # Configure the mock
        datarequest = test_data._generate_basic_datarequest()
        # Title should not be checked when it does not change
        datarequest.title = test_data.create_request_data['title'] + 'a' if title_checked else test_data.create_request_data['title']
        actions.db.DataRequest.get.return_value = [datarequest]

        # Call the action
        result = actions.datarequest_update(self.context, test_data.update_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_UPDATE, self.context, test_data.update_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=test_data.update_request_data['id'])
        expected_context = self.context.copy()
        expected_context['avoid_existing_title_check'] = not title_checked
        actions.validator.validate_datarequest.assert_called_once_with(expected_context, test_data.update_request_data)

        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once()

        self.assertEquals(datarequest.user_id, datarequest.user_id)
        self.assertEquals(test_data.update_request_data['title'], datarequest.title)
        self.assertEquals(test_data.update_request_data['description'], datarequest.description)
        self.assertEquals(test_data.update_request_data['organization_id'], datarequest.organization_id)

        # Check the result
        self._check_basic_response(datarequest, result)

    def test_datarequest_index_not_authorized(self):
        self._test_not_authorized(actions.datarequest_index, constants.DATAREQUEST_INDEX, {})

    @parameterized.expand([
        (test_data.datarequest_index_test_case_1,),
        (test_data.datarequest_index_test_case_2,),
        (test_data.datarequest_index_test_case_3,),
        (test_data.datarequest_index_test_case_4,),
        (test_data.datarequest_index_test_case_5,),
        (test_data.datarequest_index_test_case_6,),
        (test_data.datarequest_index_test_case_7,),
        (test_data.datarequest_index_test_case_8,),
        (test_data.datarequest_index_test_case_9,),
        (test_data.datarequest_index_test_case_10,),
        (test_data.datarequest_index_test_case_11,),
        (test_data.datarequest_index_test_case_12,)
    ])
    def test_datarequest_index(self, test_case):

        content = test_case['content']
        expected_ddbb_params = test_case['expected_ddbb_params']
        ddbb_response = test_case['ddbb_response']
        expected_response = test_case['expected_response']
        _organization_show = test_case['organization_show_func']

        # Set the mocks
        actions.db.DataRequest.get_ordered_by_date.return_value = ddbb_response
        organization_show = MagicMock(side_effect=_organization_show)
        actions.tk.get_action.return_value = organization_show
        
        # Call the function
        response = actions.datarequest_index(self.context, content)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_INDEX, self.context, content)
        actions.db.DataRequest.get_ordered_by_date.assert_called_once_with(**expected_ddbb_params)

        # Expected organizations_show  calls
        expected_organization_show_calls = 0

        # The initial one to get the real ID and not the name
        if 'organization_id' in content:
            organization_show.assert_any_call({'ignore_auth': True}, {'id': content['organization_id']})
            expected_organization_show_calls += 1

        # The reamining ones to include the display name into the facets
        if 'organization' in expected_response['facets']:
            expected_organization_show_calls += len(expected_response['facets']['organization']['items'])
            for organization_facet in expected_response['facets']['organization']['items']:
                organization_show.assert_any_call({'ignore_auth': True}, {'id': organization_facet['name']})

        self.assertEquals(organization_show.call_count, expected_organization_show_calls)

        # Check that the result is correct
        # We cannot execute self.assertEquals since the items in the facets
        # can have different orders
        self.assertEquals(expected_response['count'], response['count'])
        self.assertEquals(expected_response['result'], response['result'])

        for facet in expected_response['facets']:
            items = expected_response['facets'][facet]['items']

            # The response has the facet
            self.assertIn(facet, response['facets'])
            # The number of items is the same
            self.assertEquals(len(items), len(response['facets'][facet]['items']))

            # The items are the same ones
            for item in items:
                self.assertIn(item, response['facets'][facet]['items'])

    def test_datarequest_delete_not_authorized(self):
        self._test_not_authorized(actions.datarequest_delete, constants.DATAREQUEST_DELETE, test_data.delete_request_data)

    def test_datarequest_delete_not_found(self):
        self._test_not_found(actions.datarequest_delete, constants.DATAREQUEST_DELETE, test_data.delete_request_data)

    def test_datarequest_delete_no_id(self):
        self._test_no_id(actions.datarequest_delete)

    def test_datarequest_delete(self):
        # Configure the mock
        datarequest = test_data._generate_basic_datarequest()
        actions.db.DataRequest.get.return_value = [datarequest]

        # Call the function
        expected_data_dict = test_data.delete_request_data.copy()
        result = actions.datarequest_delete(self.context, test_data.delete_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_DELETE, self.context, expected_data_dict)
        self.context['session'].delete.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once_with()

        self._check_basic_response(datarequest, result)

    def test_datarequest_close_not_authorized_no_accepted_ds(self):
        self._test_not_authorized(actions.datarequest_close, constants.DATAREQUEST_CLOSE, test_data.close_request_data)

    def test_datarequest_close_not_authorized_accepted_ds(self):
        self._test_not_authorized(actions.datarequest_close, constants.DATAREQUEST_CLOSE, test_data.close_request_data_accepted_ds)

    def test_datarequest_close_no_id(self):
        self._test_no_id(actions.datarequest_close)

    def test_datarequest_close_not_found_no_accepted_ds(self):
        self._test_not_found(actions.datarequest_close, constants.DATAREQUEST_CLOSE, test_data.close_request_data)

    def test_datarequest_close_not_found_accepted_ds(self):
        self._test_not_found(actions.datarequest_close, constants.DATAREQUEST_CLOSE, test_data.close_request_data_accepted_ds)

    @parameterized.expand([
        (test_data.close_request_data, False),
        (test_data.close_request_data_accepted_ds, True)
    ])
    def test_datarequest_close(self, data, expected_accepted_ds):
        # Configure the mock
        current_time = self._datetime.datetime.now()
        actions.datetime.datetime.now = MagicMock(return_value=current_time)
        datarequest = test_data._generate_basic_datarequest()
        actions.db.DataRequest.get.return_value = [datarequest]

        # Call the function
        expected_data_dict = data.copy()
        result = actions.datarequest_close(self.context, data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CLOSE, self.context, expected_data_dict)
        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once_with()
        # The data object returned by the database has been modified appropriately
        self.assertTrue(datarequest.closed)
        self.assertEquals(datarequest.close_time, current_time)
        if expected_accepted_ds:
            self.assertEquals(datarequest.accepted_dataset, data['accepted_dataset'])
        else:
            self.assertIsNone(datarequest.accepted_dataset)

        self._check_basic_response(datarequest, result)
