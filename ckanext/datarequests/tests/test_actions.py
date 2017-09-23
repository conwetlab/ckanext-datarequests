# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016 CoNWeT Lab., Universidad Politécnica de Madrid

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
        actions.USERS_CACHE = {}
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

    def _check_comment(self, comment, response, user):
        self.assertEquals(comment.id, response['id'])
        self.assertEquals(comment.comment, response['comment'])
        self.assertEquals(str(comment.time), response['time'])
        self.assertEquals(comment.user_id, response['user_id'])
        self.assertEquals(user, response['user'])
        self.assertEquals(comment.datarequest_id, response['datarequest_id'])

    def _check_basic_response(self, datarequest, response, user, organization=None, accepted_dataset=None):
        self.assertEquals(datarequest.id, response['id'])
        self.assertEquals(datarequest.user_id, response['user_id'])
        self.assertEquals(user, response['user'])
        self.assertEquals(datarequest.title, response['title'])
        self.assertEquals(datarequest.description, response['description'])
        self.assertEquals(datarequest.organization_id, response['organization_id'])
        self.assertEquals(str(datarequest.open_time), response['open_time'])
        self.assertEquals(datarequest.closed, response['closed'])
        self.assertEquals(datarequest.accepted_dataset_id, response['accepted_dataset_id'])

        if organization:
            self.assertEquals(organization, response['organization'])

        if accepted_dataset:
            self.assertEquals(accepted_dataset, response['accepted_dataset'])

        if datarequest.close_time:
            self.assertEquals(str(datarequest.close_time), response['close_time'])
        else:
            self.assertIsNone(response['close_time'])


    ######################################################################
    ################################# AUX ################################
    ######################################################################

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
        actions.db.DataRequest.get.assert_called_once_with(id=request_data['id'])

    def _test_no_id(self, function):
        # Call the function
        with self.assertRaises(self._tk.ValidationError):
            function(self.context, {})

        # Assertions
        self.assertEquals(0, actions.db.init_db.call_count)
        self.assertEquals(0, actions.tk.check_access.call_count)
        self.assertEquals(0, actions.db.DataRequest.get.call_count)

    def _test_comment_not_found(self, function, action, request_data):
        # Configure the mock
        actions.db.Comment.get.return_value = []

        # Call the function
        with self.assertRaises(self._tk.ObjectNotFound):
            function(self.context, request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(action, self.context, request_data)
        actions.db.Comment.get.assert_called_once_with(id=request_data['id'])


    ######################################################################
    ################################# NEW ################################
    ######################################################################

    def test_create_datarequest_no_access(self):
        # Configure the mock
        actions.tk.check_access = MagicMock(side_effect=self._tk.NotAuthorized)

        # Call the function
        with self.assertRaises(self._tk.NotAuthorized):
            actions.create_datarequest(self.context, test_data.create_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.CREATE_DATAREQUEST, self.context, test_data.create_request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_create_datarequest_invalid(self):
        # Configure the mock
        actions.validator.validate_datarequest = MagicMock(side_effect=self._tk.ValidationError({'error': 'MSG ERROR'}))

        # Call the function
        with self.assertRaises(self._tk.ValidationError):
            actions.create_datarequest(self.context, test_data.create_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.CREATE_DATAREQUEST, self.context, test_data.create_request_data)
        actions.validator.validate_datarequest.assert_called_once_with(self.context, test_data.create_request_data)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_create_datarequest_valid(self):
        # Configure the mocks
        current_time = self._datetime.datetime.now()
        actions.datetime.datetime.now = MagicMock(return_value=current_time)

        # Mock actions
        default_user = {'user': 1}
        default_org = {'org': 2}
        default_pkg = None      # Accepted dataset cannot be different from None at this time
        test_data._initialize_basic_actions(actions, default_user, default_org, default_pkg)

        # Call the function
        result = actions.create_datarequest(self.context, test_data.create_request_data)

        # Assertions
        datarequest = actions.db.DataRequest.return_value

        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.CREATE_DATAREQUEST, self.context, test_data.create_request_data)
        actions.validator.validate_datarequest.assert_called_once_with(self.context, test_data.create_request_data)
        actions.db.DataRequest.assert_called_once()

        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once()

        # Check the object stored in the database
        self.assertEquals(self.context['auth_user_obj'].id, datarequest.user_id)
        self.assertEquals(test_data.create_request_data['title'], datarequest.title)
        self.assertEquals(test_data.create_request_data['description'], datarequest.description)
        self.assertEquals(test_data.create_request_data['organization_id'], datarequest.organization_id)
        self.assertEquals(current_time, datarequest.open_time)

        # Check the returned object
        self._check_basic_response(datarequest, result, default_user, default_org, default_pkg)


    ######################################################################
    ################################ SHOW ################################
    ######################################################################

    def test_show_datarequest_not_authorized(self):
        self._test_not_authorized(actions.show_datarequest, constants.SHOW_DATAREQUEST, test_data.show_request_data)

    def test_show_datarequest_not_found(self):
        self._test_not_found(actions.show_datarequest, constants.SHOW_DATAREQUEST, test_data.show_request_data)

    def test_show_datarequest_no_id(self):
        self._test_no_id(actions.show_datarequest)

    def _test_show_datarequest_found(self, datarequest, org_checked, pkg_checked):
        # Configure mock
        actions.db.DataRequest.get.return_value = [datarequest]

        # Mock actions
        default_pkg = {'pkg': 1}
        default_org = {'org': 2}
        default_user = {'user': 3}
        test_data._initialize_basic_actions(actions, default_user, default_org, default_pkg)

        # Call the function
        result = actions.show_datarequest(self.context, test_data.show_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.SHOW_DATAREQUEST, self.context, test_data.show_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=test_data.show_request_data['id'])

        org = default_org if org_checked else None
        pkg = default_pkg if pkg_checked else None
        self._check_basic_response(datarequest, result, default_user, org, pkg)

    def test_show_datarequest_found_org_open(self):
        datarequest = test_data._generate_basic_datarequest()
        self._test_show_datarequest_found(datarequest, True, False)

    def test_show_datarequest_found_no_org_open(self):
        datarequest = test_data._generate_basic_datarequest()
        datarequest['organization_id'] = None
        self._test_show_datarequest_found(datarequest, False, False)

    @parameterized.expand([
        (None,     None),
        ('org_id', None),
        (None,     'pkg_id'),
        ('org_id', 'pkg_id')
    ])
    def test_show_datarequest_found_closed(self, organization_id, accepted_dataset_id):
        datarequest = test_data._generate_basic_datarequest()
        datarequest.organization_id = organization_id
        datarequest.accepted_dataset_id = 'example_uuidv4_package'
        datarequest.close_time = datetime.datetime.now()
        datarequest.closed = True

        org_checked = True if organization_id else False
        pkg_checked = True if accepted_dataset_id else False

        self._test_show_datarequest_found(datarequest, org_checked, pkg_checked)


    ######################################################################
    ############################### UPDATE ###############################
    ######################################################################

    def test_update_datarequest_not_authorized(self):
        self._test_not_authorized(actions.update_datarequest, constants.UPDATE_DATAREQUEST, test_data.update_request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_update_datarequest_no_id(self):
        self._test_no_id(actions.update_datarequest)

    def test_update_datarequest_not_found(self):
        self._test_not_found(actions.update_datarequest, constants.UPDATE_DATAREQUEST, test_data.update_request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    @parameterized.expand([
        (True,),
        # Title checked does not depends on the organization and the dataset returned.
        # For this reason it is not necessary to execute the test with all the possible combinations
        (False,),
        (False, 'org_id', None),
        (False, None,     'pkg_id'),
        (False, 'org_id', 'pkg_id')
    ])
    def test_update_datarequest(self, title_checked, organization_id=None, accepted_dataset_id=None):
        # Configure the mock
        datarequest = test_data._generate_basic_datarequest()
        datarequest.organization_id = organization_id
        datarequest.accepted_dataset_id = accepted_dataset_id
        # Title should not be checked when it does not change
        datarequest.title = test_data.create_request_data['title'] + 'a' if title_checked else test_data.create_request_data['title']
        actions.db.DataRequest.get.return_value = [datarequest]

        # Mock actions
        default_pkg = {'pkg': 1}
        default_org = {'org': 2}
        default_user = {'user': 3}
        test_data._initialize_basic_actions(actions, default_user, default_org, default_pkg)

        # Store previous user (needed to check that it has not been modified)
        previous_user_id = datarequest.user_id

        # Call the action
        result = actions.update_datarequest(self.context, test_data.update_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.UPDATE_DATAREQUEST, self.context, test_data.update_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=test_data.update_request_data['id'])
        expected_context = self.context.copy()
        expected_context['avoid_existing_title_check'] = not title_checked
        actions.validator.validate_datarequest.assert_called_once_with(expected_context, test_data.update_request_data)

        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once()

        # Check the object stored in the database
        self.assertEquals(previous_user_id, datarequest.user_id)
        self.assertEquals(test_data.update_request_data['title'], datarequest.title)
        self.assertEquals(test_data.update_request_data['description'], datarequest.description)
        self.assertEquals(test_data.update_request_data['organization_id'], datarequest.organization_id)

        # Check the result
        org = default_org if organization_id else None
        pkg = default_pkg if accepted_dataset_id else None
        self._check_basic_response(datarequest, result, default_user, org, pkg)


    ######################################################################
    ################################ INDEX ###############################
    ######################################################################

    def test_list_datarequests_not_authorized(self):
        self._test_not_authorized(actions.list_datarequests, constants.LIST_DATAREQUESTS, {})

    @parameterized.expand([
        (test_data.list_datarequests_test_case_1,),
        (test_data.list_datarequests_test_case_2,),
        (test_data.list_datarequests_test_case_3,),
        (test_data.list_datarequests_test_case_4,),
        (test_data.list_datarequests_test_case_5,),
        (test_data.list_datarequests_test_case_6,),
        (test_data.list_datarequests_test_case_7,),
        (test_data.list_datarequests_test_case_8,),
        (test_data.list_datarequests_test_case_9,),
        (test_data.list_datarequests_test_case_10,),
        (test_data.list_datarequests_test_case_11,),
        (test_data.list_datarequests_test_case_12,),
        (test_data.list_datarequests_test_case_13,),
        (test_data.list_datarequests_test_case_14,),
        (test_data.list_datarequests_test_case_15,),
        (test_data.list_datarequests_test_case_16,),
        (test_data.list_datarequests_test_case_17,)
    ])
    def test_list_datarequests(self, test_case):

        content = test_case['content']
        expected_ddbb_params = test_case['expected_ddbb_params']
        ddbb_response = test_case['ddbb_response']
        expected_response = test_case['expected_response']
        _organization_show = test_case['organization_show_func']
        _user_show = test_case.get('user_show_func', None)

        # Set the mocks
        actions.db.DataRequest.get_ordered_by_date.return_value = ddbb_response
        actions.db.DataRequestFollower.get_datarequest_followers_number.return_value = test_data.DEFAULT_FOLLOWERS
        default_pkg = {'pkg': 1}
        default_org = {'org': 2}
        default_user = {'user': 3, 'id': test_data.user_default_id}
        test_data._initialize_basic_actions(actions, default_user, default_org, default_pkg)
        actions.tk._ = lambda x: x

        # Modify the default behaviour of 'organization_show'
        organization_show = actions.tk.get_action('organization_show')
        organization_show.side_effect = _organization_show

        # Call the function
        response = actions.list_datarequests(self.context, content)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.LIST_DATAREQUESTS, self.context, content)
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

        # We have to substract the number of times that the function is called to parse
        # the datarequest that will be returned
        count = 0
        datarequests = expected_response['result']
        for datarequest in datarequests:
            if datarequest['organization_id']:
                count += 1
            datarequest['user'] = default_user

        # Assert that organization_show has been called the appropriate number of times
        self.assertEquals(organization_show.call_count - count, expected_organization_show_calls)

        # user, organization and accepted_dataset are None by default. The value of these fields
        # must be set based on the value returned by the defined actions
        for datarequest in datarequests:
            datarequest['user'] = default_user
            datarequest['accepted_dataset'] = None
            organization_id = datarequest['organization_id']
            datarequest['organization'] = _organization_show(None, {'id': organization_id}) if organization_id else None

        # Check that the result is correct
        # We cannot execute self.assertEquals (for facets) because items
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


    ######################################################################
    ############################### DELETE ###############################
    ######################################################################

    def test_delete_datarequest_not_authorized(self):
        self._test_not_authorized(actions.delete_datarequest, constants.DELETE_DATAREQUEST, test_data.delete_request_data)

    def test_delete_datarequest_not_found(self):
        self._test_not_found(actions.delete_datarequest, constants.DELETE_DATAREQUEST, test_data.delete_request_data)

    def test_delete_datarequest_no_id(self):
        self._test_no_id(actions.delete_datarequest)

    @parameterized.expand([
        (None,     None),
        ('org_id', None),
        (None,     'pkg_id'),
        ('org_id', 'pkg_id')
    ])
    def test_delete_datarequest(self, organization_id, accepted_dataset_id):
        # Configure the mock
        datarequest = test_data._generate_basic_datarequest()
        datarequest.organization_id = organization_id
        datarequest.accepted_dataset_id = accepted_dataset_id
        actions.db.DataRequest.get.return_value = [datarequest]

        default_pkg = {'pkg': 1}
        default_org = {'org': 2}
        default_user = {'user': 3}
        test_data._initialize_basic_actions(actions, default_user, default_org, default_pkg)

        # Call the function
        expected_data_dict = test_data.delete_request_data.copy()
        result = actions.delete_datarequest(self.context, test_data.delete_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DELETE_DATAREQUEST, self.context, expected_data_dict)
        self.context['session'].delete.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once_with()

        org = default_org if organization_id else None
        pkg = default_pkg if accepted_dataset_id else None
        self._check_basic_response(datarequest, result, default_user, org, pkg)


    ######################################################################
    ################################ CLOSE ###############################
    ######################################################################

    def test_close_datarequest_not_authorized_no_accepted_ds(self):
        self._test_not_authorized(actions.close_datarequest, constants.CLOSE_DATAREQUEST, test_data.close_request_data)

    def test_close_datarequest_not_authorized_accepted_ds(self):
        self._test_not_authorized(actions.close_datarequest, constants.CLOSE_DATAREQUEST, test_data.close_request_data_accepted_ds)

    def test_close_datarequest_no_id(self):
        self._test_no_id(actions.close_datarequest)

    def test_close_datarequest_not_found_no_accepted_ds(self):
        self._test_not_found(actions.close_datarequest, constants.CLOSE_DATAREQUEST, test_data.close_request_data)

    def test_close_datarequest_not_found_accepted_ds(self):
        self._test_not_found(actions.close_datarequest, constants.CLOSE_DATAREQUEST, test_data.close_request_data_accepted_ds)

    @parameterized.expand([
        (test_data.close_request_data, False, None),
        (test_data.close_request_data_accepted_ds, True, None),
        (test_data.close_request_data, False, 'org_id'),
        (test_data.close_request_data_accepted_ds, True, 'org_id')
    ])
    def test_close_datarequest(self, data, expected_accepted_ds, organization_id):
        # Configure the mock
        current_time = self._datetime.datetime.now()
        actions.datetime.datetime.now = MagicMock(return_value=current_time)
        datarequest = test_data._generate_basic_datarequest()
        datarequest.organization_id = organization_id
        datarequest.accepted_dataset_id = None
        actions.db.DataRequest.get.return_value = [datarequest]

        # Mock actions
        default_pkg = {'pkg': 1}
        default_org = {'org': 2}
        default_user = {'user': 3}
        test_data._initialize_basic_actions(actions, default_user, default_org, default_pkg)

        # Call the function
        expected_data_dict = data.copy()
        result = actions.close_datarequest(self.context, data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.CLOSE_DATAREQUEST, self.context, expected_data_dict)
        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once_with()

        # The data object returned by the database has been modified appropriately
        self.assertTrue(datarequest.closed)
        self.assertEquals(datarequest.close_time, current_time)
        if expected_accepted_ds:
            self.assertEquals(datarequest.accepted_dataset_id, data['accepted_dataset_id'])
        else:
            self.assertIsNone(datarequest.accepted_dataset_id)

        org = default_org if organization_id else None
        pkg = default_pkg if expected_accepted_ds else None
        self._check_basic_response(datarequest, result, default_user, org, pkg)


    ######################################################################
    ############################### COMMENT ##############################
    ######################################################################

    def test_comment_not_authorized(self):
        self._test_not_authorized(actions.comment_datarequest, constants.COMMENT_DATAREQUEST, test_data.comment_request_data)

    def test_comment_no_id(self):
        self._test_no_id(actions.comment_datarequest)

    def test_comment_invalid(self, function=actions.comment_datarequest, check_access=constants.COMMENT_DATAREQUEST, 
                             request_data=test_data.comment_request_data):
        '''
        This function is also used to check invalid content when a comment is updated
        '''
        # Configure the mock
        actions.validator.validate_comment = MagicMock(side_effect=self._tk.ValidationError({'error': 'MSG ERROR'}))

        # Call the function
        with self.assertRaises(self._tk.ValidationError):
            function(self.context, request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(check_access, self.context, request_data)
        actions.validator.validate_comment.assert_called_once_with(self.context, request_data)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_comment(self):
        # Configure the mocks
        current_time = self._datetime.datetime.now()
        actions.datetime.datetime.now = MagicMock(return_value=current_time)

        # User
        default_user = {'user': 'value'}
        test_data._initialize_basic_actions(actions, default_user, None, None)

        # Call the function
        result = actions.comment_datarequest(self.context, test_data.comment_request_data)

        # Assertions
        comment = actions.db.Comment.return_value

        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access(constants.COMMENT_DATAREQUEST, self.context, test_data.comment_request_data)
        actions.validator.validate_comment.assert_called_once_with(self.context, test_data.comment_request_data)
        actions.db.Comment.assert_called_once()

        self.context['session'].add.assert_called_once_with(comment)
        self.context['session'].commit.assert_called_once()

        # Check the object stored in the database
        self.assertEquals(self.context['auth_user_obj'].id, comment.user_id)
        self.assertEquals(test_data.comment_request_data['comment'], comment.comment)
        self.assertEquals(test_data.comment_request_data['datarequest_id'], comment.datarequest_id)
        self.assertEquals(current_time, comment.time)

        # Check that the response is OK
        self._check_comment(comment, result, default_user)


    ######################################################################
    ############################ SHOW COMMENT ############################
    ######################################################################

    def test_comment_show_not_authorized(self):
        self._test_not_authorized(actions.show_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT, test_data.comment_show_request_data)

    def test_comment_show_no_id(self):
        self._test_no_id(actions.show_datarequest_comment)

    def test_comment_show_not_found(self):
        self._test_comment_not_found(actions.show_datarequest_comment, constants.SHOW_DATAREQUEST_COMMENT, test_data.comment_show_request_data)

    def test_comment_show(self):
        # Configure mock
        comment = test_data._generate_basic_comment()
        actions.db.Comment.get.return_value = [comment]

        # User
        default_user = {'user': 'value'}
        test_data._initialize_basic_actions(actions, default_user, None, None)

        # Call the function
        result = actions.show_datarequest_comment(self.context, test_data.comment_show_request_data)

        # Check that the response is OK
        self._check_comment(comment, result, default_user)


    ######################################################################
    ############################ LIST COMMENTS ###########################
    ######################################################################

    def test_comment_list_not_authorized(self):
        self._test_not_authorized(actions.list_datarequest_comments, constants.LIST_DATAREQUEST_COMMENTS, test_data.comment_list_request_data)

    def test_comment_list_no_id(self):
        self._test_no_id(actions.list_datarequest_comments)

    @parameterized.expand([
        (),
        ('asc'),
        ('desc', True),
        ('invalid')
    ])
    def test_comment_list(self, sort=None, desc=False):
        # Configure mock
        comments = []
        for i in range(0, 5):
            comments.append(test_data._generate_basic_comment())

        actions.db.Comment.get_ordered_by_date.return_value = comments

        # User
        default_user = {'user': 'value'}
        test_data._initialize_basic_actions(actions, default_user, None, None)

        # Call the function
        params = test_data.comment_show_request_data.copy()
        params.pop('id')

        if sort:
            params['sort'] = sort

        results = actions.list_datarequest_comments(self.context, params)

        # Check that the DB has been called appropriately
        actions.db.Comment.get_ordered_by_date.assert_called_once_with(datarequest_id=test_data.comment_show_request_data['datarequest_id'],
                                                                       desc=desc)

        # Check that the response is OK
        for i in range(0, len(results)):
            self._check_comment(comments[i], results[i], default_user)


    ######################################################################
    ########################### UPDATE COMMENT ###########################
    ######################################################################

    def test_comment_update_not_authorized(self):
        self._test_not_authorized(actions.update_datarequest_comment, constants.UPDATE_DATAREQUEST_COMMENT,
                                  test_data.comment_update_request_data)

    def test_comment_update_no_id(self):
        self._test_no_id(actions.update_datarequest_comment)

    def test_comment_update_not_found(self):
        self._test_comment_not_found(actions.update_datarequest_comment, constants.UPDATE_DATAREQUEST_COMMENT,
                                     test_data.comment_update_request_data)

    def test_comment_update_invalid(self):
        # The same function as the one used to check invalid content when
        # a comment is created but with appropriate parameters
        self.test_comment_invalid(actions.update_datarequest_comment, constants.UPDATE_DATAREQUEST_COMMENT,
                                  test_data.comment_update_request_data)

    def test_comment_update(self):
        # Configure the mock
        comment = test_data._generate_basic_comment(id=test_data.comment_update_request_data['id'])
        actions.db.Comment.get.return_value = [comment]

        # Mock actions
        default_user = {'user': 'value'}
        test_data._initialize_basic_actions(actions, default_user, None, None)

        # Store previous user (needed to check that it has not been modified)
        previous_user_id = comment.user_id

        # Call the action
        result = actions.update_datarequest_comment(self.context, test_data.comment_update_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.UPDATE_DATAREQUEST_COMMENT, self.context, test_data.comment_update_request_data)
        actions.db.Comment.get.assert_called_once_with(id=test_data.comment_update_request_data['id'])
        actions.validator.validate_comment.assert_called_once_with(self.context, test_data.comment_update_request_data)

        self.context['session'].add.assert_called_once_with(comment)
        self.context['session'].commit.assert_called_once()

        # Check the object stored in the database
        self.assertEquals(previous_user_id, comment.user_id)
        self.assertEquals(test_data.comment_update_request_data['datarequest_id'], comment.datarequest_id)
        self.assertEquals(test_data.comment_update_request_data['comment'], comment.comment)

        # Check the result
        self._check_comment(comment, result, default_user)


    ######################################################################
    ########################### DELETE COMMENT ###########################
    ######################################################################

    def test_comment_delete_not_authorized(self):
        self._test_not_authorized(actions.delete_datarequest_comment, constants.DELETE_DATAREQUEST_COMMENT, test_data.comment_delete_request_data)

    def test_comment_delete_no_id(self):
        self._test_no_id(actions.delete_datarequest_comment)

    def test_comment_delete_not_found(self):
        self._test_comment_not_found(actions.delete_datarequest_comment, constants.DELETE_DATAREQUEST_COMMENT, test_data.comment_delete_request_data)

    def test_comment_delete(self):
        # Configure the mock
        comment = test_data._generate_basic_comment(id=test_data.comment_update_request_data['id'])
        actions.db.Comment.get.return_value = [comment]

        default_user = {'user': 'value'}
        test_data._initialize_basic_actions(actions, default_user, None, None)

        # Call the function
        expected_data_dict = test_data.comment_delete_request_data.copy()
        result = actions.delete_datarequest_comment(self.context, test_data.comment_delete_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DELETE_DATAREQUEST_COMMENT, self.context, expected_data_dict)
        self.context['session'].delete.assert_called_once_with(comment)
        self.context['session'].commit.assert_called_once_with()

        self._check_comment(comment, result, default_user)
