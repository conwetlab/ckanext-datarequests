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

        self._request = controller.request
        controller.request = MagicMock()

        self._helpers = controller.helpers
        controller.helpers = MagicMock()

        self._datarequests_per_page = controller.constants.DATAREQUESTS_PER_PAGE

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
        controller.request = self._request
        controller.helpers = self._helpers
        controller.constants.DATAREQUESTS_PER_PAGE = self._datarequests_per_page

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

        self.assertEquals({}, controller.c.errors)
        self.assertEquals({}, controller.c.errors_summary)
        self.assertEquals({}, controller.c.datarequest)

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
                expected_request_data = request_data.copy()
                expected_request_data['id'] = ''
                self.assertEquals(expected_request_data, controller.c.datarequest)
                self.assertEquals(errors_summary, controller.c.errors_summary)
            else:
                self.assertEquals({}, controller.c.errors)
                self.assertEquals({}, controller.c.errors_summary)
                self.assertEquals({}, controller.c.datarequest)
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

    def test_update_not_authorized(self):
        datarequest_id = 'example_uuidv4'
        controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Call the function
        result = self.controller_instance.update(datarequest_id)

        # Assertions
        controller.tk.abort.assert_called_once_with(401, 'You are not authorized to update the Data Request %s' % datarequest_id)
        self.assertEquals(0, controller.tk.get_action.call_count)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertIsNone(result)

    def test_update_not_found(self):
        datarequest_id = 'example_uuidv4'
        controller.tk.get_action.return_value.side_effect = controller.tk.ObjectNotFound('Not found')

        # Call the function
        result = self.controller_instance.update(datarequest_id)

        # Assertions
        controller.tk.abort.assert_called_once_with(404, 'Data Request %s not found' % datarequest_id)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertIsNone(result)

    def test_update_no_post_content(self):
        datarequest_id = 'example_uuidv4'
        datarequest = {'id': 'uuid4', 'user_id': 'user_uuid4', 'title': 'example_title'}
        datarequest_show = controller.tk.get_action.return_value
        datarequest_show.return_value = datarequest

        # Call the function
        result = self.controller_instance.update(datarequest_id)

        # Assertions
        controller.tk.render.assert_called_once_with('datarequests/edit.html')
        self.assertEquals(result, controller.tk.render.return_value)

        self.assertEquals({}, controller.c.errors)
        self.assertEquals({}, controller.c.errors_summary)
        self.assertEquals(datarequest, controller.c.datarequest)
        self.assertEquals(datarequest['title'], controller.c.original_title)

    @parameterized.expand([
        (False, False),
        (True,  False),
        (True,  True)
    ])
    def test_update_post_content(self, authorized, validation_error):
        datarequest_id = 'this-represents-an-uuidv4()'

        original_dr = {
            'id': datarequest_id,
            'title': 'A completly different title',
            'description': 'Other description'
        }

        # Set up the get_action function
        datarequest_show = MagicMock(return_value=original_dr)
        datarequest_update = MagicMock()
        
        def _get_action(action):
            if action == constants.DATAREQUEST_SHOW:
                return datarequest_show
            else:
                return datarequest_update

        controller.tk.get_action.side_effect = _get_action

        # Raise exception if the user is not authorized to create a new data request
        if not authorized:
            controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Raise exception when the user input is not valid
        if validation_error:
            datarequest_update.side_effect = controller.tk.ValidationError({'Title': ['error1', 'error2'],
                                                                            'Description': ['error3, error4']})
        else:
            datarequest_update.return_value = {'id': datarequest_id}

        # Create the request
        request_data = controller.request.POST = {
            'id': datarequest_id,
            'title': 'Example Title',
            'description': 'Example Description',
            'organization_id': 'organization uuid4'
        }
        result = self.controller_instance.update(datarequest_id)

        if authorized:
            self.assertEquals(0, controller.tk.abort.call_count)
            self.assertEquals(controller.tk.render.return_value, result)
            controller.tk.render.assert_called_once_with('datarequests/edit.html')

            datarequest_show.assert_called_once_with(self.expected_context, {'id': datarequest_id})
            datarequest_update.assert_called_once_with(self.expected_context, request_data)

            if validation_error:
                errors_summary = {}
                for key, error in datarequest_update.side_effect.error_dict.items():
                    errors_summary[key] = ', '.join(error)

                self.assertEquals(datarequest_update.side_effect.error_dict, controller.c.errors)
                expected_request_data = request_data.copy()
                expected_request_data['id'] = datarequest_id
                self.assertEquals(expected_request_data, controller.c.datarequest)
                self.assertEquals(errors_summary, controller.c.errors_summary)
                self.assertEquals(original_dr['title'], controller.c.original_title)
            else:
                self.assertEquals({}, controller.c.errors)
                self.assertEquals({}, controller.c.errors_summary)
                self.assertEquals(original_dr, controller.c.datarequest)
                self.assertEquals(302, controller.tk.response.status_int)
                self.assertEquals('%s/%s' % (constants.DATAREQUESTS_MAIN_PATH, datarequest_id),
                                  controller.tk.response.location)
        else:
            controller.tk.abort.assert_called_once_with(401, 'You are not authorized to update the Data Request %s' % datarequest_id)
            self.assertEquals(0, controller.tk.render.call_count)

    def test_index_not_authorized(self):
        controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User is not authorized')

        # Call the function
        result = self.controller_instance.index()

        # Assertions
        controller.tk.abort.assert_called_once_with(401, 'Unauthorized to list Data Requests')
        self.assertEquals(0, controller.tk.get_action.call_count)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertIsNone(result)

    def test_index_invalid_page(self):
        controller.request.GET = controller.request.params = {'page': '2a'}

        # Call the function
        result = self.controller_instance.index()

        # Assertions
        controller.tk.abort.assert_called_once_with(400, '"page" parameter must be an integer')
        self.assertEquals(0, controller.tk.check_access.call_count)
        self.assertEquals(0, controller.tk.get_action.call_count)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertIsNone(result)

    @parameterized.expand([
        ('index', '1', 'conwet', 0,    10),
        ('index', '2', 'conwet', 10,   10),
        ('index', '7', 'conwet', 60,   10),
        ('index', '1', 'conwet', 0,    25, 25),
        ('index', '2', 'conwet', 25,   25, 25),
        ('index', '7', 'conwet', 150,  25, 25),
        ('index', '5', None,     40,   10),
        ('organization_datarequests', '1', 'conwet', 0,    10),
        ('organization_datarequests', '2', 'conwet', 10,   10),
        ('organization_datarequests', '7', 'conwet', 60,   10),
        ('organization_datarequests', '1', 'conwet', 0,    25, 25),
        ('organization_datarequests', '2', 'conwet', 25,   25, 25),
        ('organization_datarequests', '7', 'conwet', 150,  25, 25),
    ])
    def test_index_organization_dr(self, func, page, organization, expected_offset, expected_limit, datarequests_per_page=10):
        params = {}
        organization_show_action = 'organization_show'
        base_url = 'http://someurl.com/somepath/otherpath'

        # Expected data_dict
        expected_data_dict = {
            'offset': expected_offset,
            'limit': expected_limit
        }

        # Set datarequests_per_page
        constants.DATAREQUESTS_PER_PAGE = datarequests_per_page

        # Get parameters
        controller.request.GET = controller.request.params = {}

        # Set page
        if page:
            controller.request.GET['page'] = page

        # Set the organization in the correct place depending on the function
        if func == 'index':
            if organization:
                controller.request.GET['organization'] = organization
                expected_data_dict['organization_id'] = organization
        else:
            # organization_datarequests
            params['id'] = organization
            expected_data_dict['organization_id'] = organization

        # Mocking
        organization_show = MagicMock()
        datarequest_index = MagicMock()
        def _get_action(action):
            if action == organization_show_action:
                return organization_show
            else:
                return datarequest_index

        controller.tk.get_action.side_effect = _get_action
        controller.helpers.url_for.return_value = base_url

        # Call the function
        function = getattr(self.controller_instance, func)
        result = function(**params)

        # Assertions
        controller.tk.check_access.assert_called_once_with(constants.DATAREQUEST_INDEX, self.expected_context, expected_data_dict)        

        # Specific assertions depending on the function called
        if func == 'index':
            controller.tk.get_action.assert_called_once_with(constants.DATAREQUEST_INDEX)
            self.assertEquals(0, organization_show.call_count)
            expected_render_page = 'datarequests/index.html'
        else:
            self.assertEquals(2, controller.tk.get_action.call_count)
            controller.tk.get_action.assert_any_call(constants.DATAREQUEST_INDEX)
            controller.tk.get_action.assert_any_call(organization_show_action)
            self.assertEquals(organization_show.return_value, controller.c.group_dict)
            organization_show.assert_called_once_with(self.expected_context, {'id': organization})
            expected_render_page = 'organization/datarequests.html'

        # Check the values put in c
        datarequest_index.assert_called_once_with(self.expected_context, expected_data_dict)
        expected_response = datarequest_index.return_value
        self.assertEquals(expected_response['count'], controller.c.datarequest_count)
        self.assertEquals(expected_response['result'], controller.c.datarequests)
        self.assertEquals(expected_response['facets'], controller.c.search_facets)
        self.assertEquals(controller.helpers.Page.return_value, controller.c.page)

        # Check the pager
        page_arguments = controller.helpers.Page.call_args[1]
        self.assertEquals(datarequests_per_page, page_arguments['items_per_page'])
        self.assertEquals(int(page), page_arguments['page'])
        self.assertEquals(expected_response['count'], page_arguments['item_count'])
        self.assertEquals(expected_response['result'], page_arguments['collection'])
        silly_page = 72
        self.assertEquals("%s?page=%d" % (base_url, silly_page), page_arguments['url'](page=silly_page))

        # When URL function is called, helpers.url_for is called to get the final URL
        if func == 'index':
            controller.helpers.url_for.assert_called_once_with(
                controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                action='index')
        else:
            controller.helpers.url_for.assert_called_once_with(
                controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                action='organization_datarequests', id=organization)

        # Check the facets
        expected_facet_titles = {}
        expected_facet_titles['state'] = controller.tk._('State')
        if func == 'index':
            expected_facet_titles['organization'] = controller.tk._('Organizations')

        self.assertEquals(expected_facet_titles, controller.c.facet_titles)

        # Check that the render functions has been called with the suitable parameters
        self.assertEquals(controller.tk.render.return_value, result)
        controller.tk.render.assert_called_once_with(expected_render_page)
