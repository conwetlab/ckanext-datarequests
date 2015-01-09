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
import unittest

from mock import MagicMock

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


class ActionsTest(unittest.TestCase):

    def setUp(self):
        # Mocks
        self._tk = actions.tk
        actions.tk = MagicMock()

        self._c = actions.c
        actions.c = MagicMock()

        self._db = actions.db
        actions.db = MagicMock()

        self._validator = actions.validator
        actions.validator = MagicMock()

        self._datetime = actions.datetime
        actions.datetime = MagicMock()

    def tearDown(self):
        # Unmock
        actions.tk = self._tk
        actions.c = self._c
        actions.db = self._db
        actions.validator = self._validator
        actions.datetime = self._datetime

    def test_datarequest_create_no_access(self):
        # Configure the mock
        actions.tk.check_access = MagicMock(side_effect=self._tk.NotAuthorized)

        # Call the function
        try:
            actions.datarequest_create(context, request_data)
        except self._tk.NotAuthorized:
            pass

        # Assertions
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, context, request_data)
        self.assertEquals(0, actions.validator.validate_datarequest.call_count)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, context['session'].add.call_count)
        self.assertEquals(0, context['session'].commit.call_count)

    def test_datarequest_create_invalid(self):
        # Configure the mock
        actions.validator.validate_datarequest = MagicMock(side_effect=self._tk.ValidationError({'error': 'MSG ERROR'}))

        # Call the function
        try:
            actions.datarequest_create(context, request_data)
        except self._tk.ValidationError:
            pass

        # Assertions
        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, context, request_data)
        actions.validator.validate_datarequest.assert_called_once_with(context, request_data)
        self.assertEquals(0, actions.db.DataRequest.call_count)
        self.assertEquals(0, context['session'].add.call_count)
        self.assertEquals(0, context['session'].commit.call_count)

    def test_datarequest_create_valid(self):
        # Configure the mocks
        current_time = self._datetime.datetime.now()
        actions.datetime.datetime.now = MagicMock(return_value=current_time)

        # Call the function
        actions.datarequest_create(context, request_data)
        
        # Assertions
        datarequest = actions.db.DataRequest.return_value

        actions.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, context, request_data)
        actions.validator.validate_datarequest.assert_called_once_with(context, request_data)
        actions.db.DataRequest.assert_called_once()

        context['session'].add.assert_called_once_with(datarequest)
        context['session'].commit.assert_called_once()

        self.assertEquals(context['auth_user_obj'].id, datarequest.user_id)
        self.assertEquals(request_data['title'], datarequest.title)
        self.assertEquals(request_data['description'], datarequest.description)
        self.assertEquals(request_data['organization'], datarequest.organization)
        self.assertEquals(current_time, datarequest.open_time)
