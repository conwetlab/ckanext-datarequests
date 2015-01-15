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
import unittest

from mock import MagicMock
from nose_parameterized import parameterized


create_request_data = {
    'title': 'title',
    'description': 'description',
    'organization_id': 'organization'
}

show_request_data = {
    'id': 'example_uuidv4'
}

update_request_data = {
    'id': 'example_uuidv4',
    'title': 'title',
    'description': 'description',
    'organization_id': 'organization'
}


def _generate_basic_datarequest():
    datarequest = MagicMock()
    datarequest.id = 'example_uuidv4'
    datarequest.user_id = 'example_uuidv4_user'
    datarequest.title = 'This is a title'
    datarequest.description = 'This is a basic description'
    datarequest.organization_id = 'example_uuidv4_organization'
    datarequest.open_time = datetime.datetime.now()

    return datarequest


class ActionsTest(unittest.TestCase):

    def setUp(self):
        # Mocks
        self._tk = actions.tk
        actions.tk = MagicMock()
        actions.tk.ObjectNotFound = self._tk.ObjectNotFound

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

    def test_datarequest_create_no_access(self):
        # Configure the mock
        actions.tk.check_access = MagicMock(side_effect=self._tk.NotAuthorized)

        # Call the function
        try:
            actions.datarequest_create(self.context, create_request_data)
        except self._tk.NotAuthorized:
            pass

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, self.context, create_request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_datarequest_create_invalid(self):
        # Configure the mock
        actions.validator.validate_datarequest = MagicMock(side_effect=self._tk.ValidationError({'error': 'MSG ERROR'}))

        # Call the function
        try:
            actions.datarequest_create(self.context, create_request_data)
        except self._tk.ValidationError:
            pass

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, self.context, create_request_data)
        actions.validator.validate_datarequest.assert_called_once_with(self.context, create_request_data)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_datarequest_create_valid(self):
        # Configure the mocks
        current_time = self._datetime.datetime.now()
        actions.datetime.datetime.now = MagicMock(return_value=current_time)

        # Call the function
        result = actions.datarequest_create(self.context, create_request_data)
        
        # Assertions
        datarequest = actions.db.DataRequest.return_value

        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, self.context, create_request_data)
        actions.validator.validate_datarequest.assert_called_once_with(self.context, create_request_data)
        actions.db.DataRequest.assert_called_once()

        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once()

        self.assertEquals(self.context['auth_user_obj'].id, datarequest.user_id)
        self.assertEquals(create_request_data['title'], datarequest.title)
        self.assertEquals(create_request_data['description'], datarequest.description)
        self.assertEquals(create_request_data['organization_id'], datarequest.organization_id)
        self.assertEquals(current_time, datarequest.open_time)

        self._check_basic_response(datarequest, result)

    def test_datarequest_show_not_authorized(self):
        # Configure the mock
        actions.tk.check_access = MagicMock(side_effect=self._tk.NotAuthorized)

        # Call the function
        try:
            actions.datarequest_show(self.context, show_request_data)
        except self._tk.NotAuthorized:
            pass

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_SHOW, self.context, show_request_data)
        self.assertEquals(0, actions.db.DataRequest.get.call_count)

    def test_datarequest_not_found(self):
        # Configure the mock
        actions.db.DataRequest.get.return_value = []

        # Call the function
        try:
            actions.datarequest_show(self.context, show_request_data)
        except self._tk.ObjectNotFound:
            pass

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_SHOW, self.context, show_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=show_request_data['id'])

    def _test_datarequest_found(self, datarequest):
        # Configure mock
        actions.db.DataRequest.get.return_value = [datarequest]

        # Call the function
        result = actions.datarequest_show(self.context, show_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_SHOW, self.context, show_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=show_request_data['id'])

        self._check_basic_response(datarequest, result)
        self.assertEquals(datarequest.accepted_dataset, result['accepted_dataset'])
        expected_close_time = str(datarequest.close_time) if datarequest.close_time else None
        self.assertEquals(expected_close_time, result['close_time'])
        self.assertEquals(datarequest.closed, result['closed'])

    def test_datarequest_found_open(self):
        datarequest = _generate_basic_datarequest()
        datarequest.accepted_dataset = None
        datarequest.close_time = None
        datarequest.closed = False

        self._test_datarequest_found(datarequest)

    def test_datarequest_found_closed(self):
        datarequest = _generate_basic_datarequest()
        datarequest.accepted_dataset = 'example_uuidv4_package'
        datarequest.close_time = datetime.datetime.now()
        datarequest.closed = True

        self._test_datarequest_found(datarequest)

    def test_datarequest_update_not_authorized(self):
        # Configure the mock
        actions.tk.check_access = MagicMock(side_effect=self._tk.NotAuthorized)

        # Call the action
        with self.assertRaises(self._tk.NotAuthorized):
            actions.datarequest_update(self.context, update_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_UPDATE, self.context, update_request_data)
        self.assertEquals(0, actions.db.DataRequest.get.call_count)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    def test_datarequest_update_not_found(self):
        # Configure the mock
        actions.db.DataRequest.get.return_value = []

        # Call the action
        with self.assertRaises(self._tk.ObjectNotFound):
            actions.datarequest_update(self.context, update_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_UPDATE, self.context, update_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=update_request_data['id'])
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, self.context['session'].add.call_count)
        self.assertEquals(0, self.context['session'].commit.call_count)

    @parameterized.expand([
        (True,),
        (False,)
    ])
    def test_datarequest_update(self, title_checked):
        # Configure the mock
        datarequest = _generate_basic_datarequest()
        # Title should not be checked when it does not change
        datarequest.title = create_request_data['title'] + 'a' if title_checked else create_request_data['title']
        actions.db.DataRequest.get.return_value = [datarequest]

        # Call the action
        result = actions.datarequest_update(self.context, update_request_data)

        # Assertions
        actions.db.init_db.assert_called_once_with(self.context['model'])
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_UPDATE, self.context, update_request_data)
        actions.db.DataRequest.get.assert_called_once_with(id=update_request_data['id'])
        expected_context = self.context.copy()
        expected_context['avoid_existing_title_check'] = not title_checked
        actions.validator.validate_datarequest.assert_called_once_with(expected_context, update_request_data)

        self.context['session'].add.assert_called_once_with(datarequest)
        self.context['session'].commit.assert_called_once()

        self.assertEquals(datarequest.user_id, datarequest.user_id)
        self.assertEquals(update_request_data['title'], datarequest.title)
        self.assertEquals(update_request_data['description'], datarequest.description)
        self.assertEquals(update_request_data['organization_id'], datarequest.organization_id)

        # Check the result
        self._check_basic_response(datarequest, result)

