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
import ckanext.datarequests.controllers.ui_controller as controller
import unittest

from mock import MagicMock
from nose_parameterized import parameterized


class UIControllerTest(unittest.TestCase):

    def setUp(self):
        self._plugins = controller.plugins
        controller.plugins = MagicMock()

        self._tk = controller.tk
        controller.tk = MagicMock()
        controller.tk._ = self._tk._
        controller.tk.ValidationError = self._tk.ValidationError
        controller.tk.NotAuthorized = self._tk.NotAuthorized
        controller.tk.ObjectNotFound = self._tk.ObjectNotFound

        self._c = controller.c
        controller.c = MagicMock()

        self._request = controller.request
        controller.request = MagicMock()

        self._model = controller.model
        controller.model = MagicMock()

        self.expected_context = {
            'model': controller.model,
            'session': controller.model.Session,
            'user': controller.c.user,
            'auth_user_obj': controller.c.userobj
        }

        self.controller_instance = controller.DataRequestsUI()

    def tearDown(self):
        controller.plugins = self._plugins
        controller.tk = self._tk
        controller.c = self._c
        controller.request = self._request
        controller.model = self._model

    def test_index(self):
        result = self.controller_instance.index()
        self.assertEquals(controller.tk.render.return_value, result)
        controller.tk.render.assert_called_once_with('datarequests/index.html')

    @parameterized.expand([
        (True,),
        (False,)
    ])
    def test_new_no_post(self, authorized):
        # Raise exception if the user is not authorized to create a new data request
        if not authorized:
            controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        result = self.controller_instance.new()

        controller.tk.check_access.assert_called_once_with(constants.DATAREQUEST_CREATE, self.expected_context, None)

        if authorized:
            self.assertEquals(0, controller.tk.abort.call_count)
            self.assertEquals(controller.tk.render.return_value, result)
            controller.tk.render.assert_called_once_with('datarequests/new.html')
        else:
            controller.tk.abort.assert_called_once_with(401, 'Unauthorized to create a Data Request')
            self.assertEquals(0, controller.tk.render.call_count)

        self.assertEquals(None, controller.c.errors)
        self.assertEquals(None, controller.c.errors_summary)
        self.assertEquals(None, controller.c.datarequest)

    @parameterized.expand([
        (False, False),
        (True,  False),
        (True,  True)
    ])
    def test_new_post_content(self, authorized, validation_error):
        datarequest_id = 'this-represents-an-uuidv4()'

        # Raise exception if the user is not authorized to create a new data request
        if not authorized:
            controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Raise exception when the user input is not valid
        action = controller.tk.get_action.return_value
        if validation_error:
            action.side_effect = controller.tk.ValidationError({'Title': ['error1', 'error2'],
                                                                'Description': ['error3, error4']})
        else:
            action.return_value = {'id': datarequest_id}

        # Create the request
        request_data = controller.request.POST = {
            'title': 'Example Title',
            'description': 'Example Description',
            'organization_id': 'organization uuid4'
        }
        result = self.controller_instance.new()

        if authorized:
            self.assertEquals(0, controller.tk.abort.call_count)
            self.assertEquals(controller.tk.render.return_value, result)
            controller.tk.render.assert_called_once_with('datarequests/new.html')

            controller.tk.get_action.return_value.assert_called_once_with(self.expected_context, request_data)

            if validation_error:
                errors_summary = {}
                for key, error in action.side_effect.error_dict.items():
                    errors_summary[key] = ', '.join(error)

                self.assertEquals(action.side_effect.error_dict, controller.c.errors)
                self.assertEquals(request_data, controller.c.datarequest)
                self.assertEquals(errors_summary, controller.c.errors_summary)
            else:
                self.assertEquals(None, controller.c.errors)
                self.assertEquals(None, controller.c.errors_summary)
                self.assertEquals(None, controller.c.datarequest)
                self.assertEquals(302, controller.tk.response.status_int)
                self.assertEquals('%s/%s' % (constants.DATAREQUESTS_MAIN_PATH, datarequest_id),
                                  controller.tk.response.location)
        else:
            controller.tk.abort.assert_called_once_with(401, 'Unauthorized to create a Data Request')
            self.assertEquals(0, controller.tk.render.call_count)

    def test_show_not_authorized(self):
        datarequest_id = 'example_uuidv4'
        controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Call the function
        result = self.controller_instance.show(datarequest_id)

        # Assertions
        controller.tk.abort.assert_called_once_with(401, 'You are not authorized to view the Data Request %s' % datarequest_id)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertIsNone(result)

    def test_show_not_found(self):
        datarequest_id = 'example_uuidv4'
        controller.tk.get_action.return_value.side_effect = controller.tk.ObjectNotFound('Data set not found')

        # Call the function
        result = self.controller_instance.show(datarequest_id)

        # Assertions
        controller.tk.abort.assert_called_once_with(404, 'Data Request %s not found' % datarequest_id)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertIsNone(result)

    @parameterized.expand({
        (False, False),
        (False, True),
        (True,  False),
        (True,  True)
    })
    def test_show_found(self, user_show_exception, organization_show_exception):
        datarequest_id = 'example_uuidv4'
        datarequest_show = MagicMock(return_value={
            'id': 'example_uuidv4',
            'user_id': 'example_uuidv4_user',
            'organization_id': 'example_uuidv4_organization'
        })

        default_user = {'display_name': 'User Display Name'}
        default_organization = {'display_name': 'Organization Name'}

        def _user_show(context, data_request):
            if user_show_exception:
                raise controller.tk.ObjectNotFound('User not Found')
            else:
                return default_user

        def _organization_show(context, data_request):
            if organization_show_exception:
                raise controller.tk.ObjectNotFound('Organization not Found')
            else:
                return default_organization

        user_show = MagicMock(side_effect=_user_show)
        organization_show = MagicMock(side_effect=_organization_show)

        def _get_action(action):
            if action == 'datarequest_show':
                return datarequest_show
            elif action == 'user_show':
                return user_show
            elif action == 'organization_show':
                return organization_show

        controller.tk.get_action.side_effect = _get_action

        # Call the function
        result = self.controller_instance.show(datarequest_id)

        # Assertions
        expected_datarequest = datarequest_show.return_value.copy()
        if not user_show_exception:
            expected_datarequest['user'] = default_user
        if not organization_show_exception:
            expected_datarequest['organization'] = default_organization
        self.assertEquals(expected_datarequest, controller.c.datarequest)
        controller.tk.render.assert_called_once_with('datarequests/show.html')
        self.assertEquals(controller.tk.render.return_value, result)
