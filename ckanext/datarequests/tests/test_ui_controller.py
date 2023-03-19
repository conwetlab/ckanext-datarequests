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

from ckanext.datarequests import constants, request_helpers
import ckanext.datarequests.controllers.controller_functions as controller
import unittest

from mock import MagicMock
from parameterized import parameterized


INDEX_FUNCTION = 'index'
ORGANIZATION_DATAREQUESTS_FUNCTION = 'organization'
USER_DATAREQUESTS_FUNCTION = 'user'


def _patch_GET(params):
    request_helpers.request.GET = params
    request_helpers.request.args = params
    return params


def _patch_POST(params):
    request_helpers.request.POST = params
    request_helpers.request.form = params
    return params


class UIControllerTest(unittest.TestCase):

    def setUp(self):
        self._tk = controller.tk
        controller.tk = MagicMock()
        controller.tk._ = self._tk._
        controller.tk.ValidationError = self._tk.ValidationError
        controller.tk.NotAuthorized = self._tk.NotAuthorized
        controller.tk.ObjectNotFound = self._tk.ObjectNotFound
        controller.tk.abort.return_value = 'aborted'

        self._c = controller.c
        controller.c = MagicMock()

        self._request = request_helpers.request
        request_helpers.request = MagicMock()

        self._model = controller.model
        controller.model = MagicMock()

        self._helpers = controller.helpers
        controller.helpers = MagicMock()

        self._h = controller.h
        controller.h = MagicMock()

        self.expected_context = {
            'model': controller.model,
            'session': controller.model.Session,
            'user': controller.c.user,
            'auth_user_obj': controller.c.userobj
        }

    def tearDown(self):
        controller.tk = self._tk
        controller.c = self._c
        request_helpers.request = self._request
        controller.model = self._model
        controller.helpers = self._helpers
        controller.h = self._h

    ######################################################################
    ################################# AUX ################################
    ######################################################################

    def _test_not_authorized(self, function, action, check_access_func):
        datarequest_id = 'example_uuidv4'
        controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Call the function
        result = function(datarequest_id)

        # Assertions
        controller.tk.check_access.assert_called_once_with(check_access_func, self.expected_context, {'id': datarequest_id})
        controller.tk.abort.assert_called_once_with(403, 'You are not authorized to %s the Data Request %s' % (action, datarequest_id))
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    def _test_not_found(self, function, get_action_func):
        datarequest_id = 'example_uuidv4'

        def _get_action(action):
            if action == get_action_func:
                return MagicMock(side_effect=controller.tk.ObjectNotFound('Data set not found'))
            elif action == constants.SHOW_DATAREQUEST:
                # test_close_not_found needs show_datarequest to return closed = False to work
                return MagicMock(return_value={'closed': False})

        controller.tk.get_action.side_effect = _get_action

        # Call the function
        result = function(datarequest_id)

        # Assertions
        controller.tk.get_action.assert_any_call(get_action_func)
        controller.tk.abort.assert_called_once_with(404, 'Data Request %s not found' % datarequest_id)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    ######################################################################
    ################################# NEW ################################
    ######################################################################

    @parameterized.expand([
        (True,),
        (False,)
    ])
    def test_new_no_post(self, authorized):
        controller.tk.response.location = None
        controller.tk.response.status_int = 200
        _patch_POST({})

        # Raise exception if the user is not authorized to create a new data request
        if not authorized:
            controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        result = controller.new()

        controller.tk.check_access.assert_called_once_with(constants.CREATE_DATAREQUEST, self.expected_context, None)

        if authorized:
            self.assertEquals(0, controller.tk.abort.call_count)
            self.assertEquals(controller.tk.render.return_value, result)
            controller.tk.render.assert_called_once_with('datarequests/new.html')
        else:
            controller.tk.abort.assert_called_once_with(403, 'Unauthorized to create a Data Request')
            self.assertEquals(0, controller.tk.render.call_count)

        self.assertIsNone(controller.tk.response.location)
        self.assertEquals(200, controller.tk.response.status_int)
        self.assertEquals({}, controller.c.errors)
        self.assertEquals({}, controller.c.errors_summary)
        self.assertEquals({}, controller.c.datarequest)

    @parameterized.expand([
        (False, False),
        (True, False),
        (True, True)
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
        request_data = _patch_POST({
            'title': 'Example Title',
            'description': 'Example Description',
            'organization_id': 'organization uuid4'
        })
        result = controller.new()

        # Authorize function has been called
        controller.tk.check_access.assert_called_once_with(constants.CREATE_DATAREQUEST,
                                                           self.expected_context, None)

        if authorized:
            self.assertEquals(0, controller.tk.abort.call_count)
            if validation_error:
                self.assertEquals(controller.tk.render.return_value, result)
                controller.tk.render.assert_called_once_with('datarequests/new.html')
            else:
                self.assertEquals(controller.tk.redirect_to.return_value, result)
                self.assertEquals(0, controller.tk.render.call_count)

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
                controller.tk.url_for.assert_called_once_with(
                    'datarequest.show', id=datarequest_id)
                controller.tk.redirect_to.assert_called_once_with(controller.tk.url_for.return_value)
        else:
            controller.tk.abort.assert_called_once_with(403, 'Unauthorized to create a Data Request')
            self.assertEquals(0, controller.tk.render.call_count)

    ######################################################################
    ################################ SHOW ################################
    ######################################################################

    def test_show_not_authorized(self):
        self._test_not_authorized(controller.show, 'view', constants.SHOW_DATAREQUEST)

    def test_show_not_found(self):
        self._test_not_found(controller.show, constants.SHOW_DATAREQUEST)

    @parameterized.expand({
        (False, False, None),
        (False, True, None),
        (True, False, None),
        (True, True, None),
        (False, False, 'uudiv4', False),
        (False, True, 'uudiv4', False),
        (True, False, 'uudiv4', False),
        (True, True, 'uudiv4', False),
        (False, False, 'uudiv4', True),
        (False, True, 'uudiv4', True),
        (True, False, 'uudiv4', True),
        (True, True, 'uudiv4', True)
    })
    def test_show_found(self, user_show_exception, organization_show_exception, accepted_dataset, package_show_exception=False):

        datarequest_id = 'example_uuidv4'
        default_user = {'display_name': 'User Display Name'}
        default_organization = {'display_name': 'Organization Name'}
        default_package = {'title': 'Package'}

        show_datarequest = MagicMock(return_value={
            'id': 'example_uuidv4',
            'user_id': 'example_uuidv4_user',
            'organization_id': 'example_uuidv4_organization',
            'accepted_dataset_id': accepted_dataset,
            'user': default_user,
            'organization': default_organization,
            'accepted_dataset': default_package
        })

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

        def _package_show(context, data_request):
            if package_show_exception:
                raise controller.tk.ObjectNotFound('Package nof Found')
            else:
                return default_package

        user_show = MagicMock(side_effect=_user_show)
        organization_show = MagicMock(side_effect=_organization_show)
        package_show = MagicMock(side_effect=_package_show)

        def _get_action(action):
            if action == 'show_datarequest':
                return show_datarequest
            elif action == 'user_show':
                return user_show
            elif action == 'organization_show':
                return organization_show
            elif action == 'package_show':
                return package_show

        controller.tk.get_action.side_effect = _get_action

        # Call the function
        result = controller.show(datarequest_id)

        # Authorize function has been called
        controller.tk.check_access.assert_called_once_with(constants.SHOW_DATAREQUEST, self.expected_context,
                                                           {'id': datarequest_id})

        # Assertions
        expected_datarequest = show_datarequest.return_value.copy()
        if not user_show_exception:
            expected_datarequest['user'] = default_user
        if not organization_show_exception:
            expected_datarequest['organization'] = default_organization
        if not package_show_exception and accepted_dataset:
            expected_datarequest['accepted_dataset'] = default_package
        self.assertEquals(expected_datarequest, controller.c.datarequest)
        controller.tk.render.assert_called_once_with('datarequests/show.html')
        self.assertEquals(controller.tk.render.return_value, result)

    ######################################################################
    ############################### UPDATE ###############################
    ######################################################################

    def test_update_not_authorized(self):
        self._test_not_authorized(controller.update, 'update', constants.UPDATE_DATAREQUEST)

    def test_update_not_found(self):
        self._test_not_found(controller.update, constants.UPDATE_DATAREQUEST)

    def test_update_no_post_content(self):
        controller.tk.response.location = None
        controller.tk.response.status_int = 200
        _patch_POST({})

        datarequest_id = 'example_uuidv4'
        datarequest = {'id': 'uuid4', 'user_id': 'user_uuid4', 'title': 'example_title'}
        show_datarequest = controller.tk.get_action.return_value
        show_datarequest.return_value = datarequest

        # Call the function
        result = controller.update(datarequest_id)

        # Authorize function has been called
        controller.tk.check_access.assert_called_once_with(constants.UPDATE_DATAREQUEST, self.expected_context, {'id': datarequest_id})

        # Assertions
        controller.tk.render.assert_called_once_with('datarequests/edit.html')
        self.assertEquals(result, controller.tk.render.return_value)

        self.assertIsNone(controller.tk.response.location)
        self.assertEquals(200, controller.tk.response.status_int)
        self.assertEquals({}, controller.c.errors)
        self.assertEquals({}, controller.c.errors_summary)
        self.assertEquals(datarequest, controller.c.datarequest)
        self.assertEquals(datarequest['title'], controller.c.original_title)

    @parameterized.expand([
        (False, False),
        (True, False),
        (True, True)
    ])
    def test_update_post_content(self, authorized, validation_error):
        datarequest_id = 'this-represents-an-uuidv4()'

        original_dr = {
            'id': datarequest_id,
            'title': 'A completely different title',
            'description': 'Other description'
        }

        # Set up the get_action function
        show_datarequest = MagicMock(return_value=original_dr)
        update_datarequest = MagicMock()

        def _get_action(action):
            if action == constants.SHOW_DATAREQUEST:
                return show_datarequest
            else:
                return update_datarequest

        controller.tk.get_action.side_effect = _get_action

        # Raise exception if the user is not authorized to create a new data request
        if not authorized:
            controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Raise exception when the user input is not valid
        if validation_error:
            update_datarequest.side_effect = controller.tk.ValidationError({'Title': ['error1', 'error2'],
                                                                            'Description': ['error3, error4']})
        else:
            update_datarequest.return_value = {'id': datarequest_id}

        # Create the request
        request_data = _patch_POST({
            'id': datarequest_id,
            'title': 'Example Title',
            'description': 'Example Description',
            'organization_id': 'organization uuid4'
        })
        result = controller.update(datarequest_id)

        # Authorize function has been called
        controller.tk.check_access.assert_called_once_with(constants.UPDATE_DATAREQUEST, self.expected_context, {'id': datarequest_id})

        if authorized:
            self.assertEquals(0, controller.tk.abort.call_count)

            show_datarequest.assert_called_once_with(self.expected_context, {'id': datarequest_id})
            update_datarequest.assert_called_once_with(self.expected_context, request_data)

            if validation_error:
                errors_summary = {}
                for key, error in update_datarequest.side_effect.error_dict.items():
                    errors_summary[key] = ', '.join(error)

                self.assertEquals(update_datarequest.side_effect.error_dict, controller.c.errors)
                expected_request_data = request_data.copy()
                expected_request_data['id'] = datarequest_id
                self.assertEquals(expected_request_data, controller.c.datarequest)
                self.assertEquals(errors_summary, controller.c.errors_summary)
                self.assertEquals(original_dr['title'], controller.c.original_title)
                self.assertEquals(controller.tk.render.return_value, result)
                controller.tk.render.assert_called_once_with('datarequests/edit.html')
            else:
                self.assertEquals({}, controller.c.errors)
                self.assertEquals({}, controller.c.errors_summary)
                self.assertEquals(original_dr, controller.c.datarequest)
                self.assertEquals(controller.tk.redirect_to.return_value, result)
                controller.tk.url_for.assert_called_once_with(
                    'datarequest.show', id=datarequest_id)
                controller.tk.redirect_to.assert_called_once_with(controller.tk.url_for.return_value)
        else:
            controller.tk.abort.assert_called_once_with(403, 'You are not authorized to update the Data Request %s' % datarequest_id)
            self.assertEquals(0, controller.tk.render.call_count)

    ######################################################################
    ################################ INDEX ###############################
    ######################################################################

    def test_index_not_authorized(self):
        controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User is not authorized')
        organization_name = 'org'
        _patch_GET({'organization': organization_name})

        # Call the function
        result = controller.index()

        # Assertions
        expected_data_req = {'organization_id': organization_name, 'limit': 10, 'offset': 0, 'sort': 'desc'}
        controller.tk.check_access.assert_called_once_with(constants.LIST_DATAREQUESTS, self.expected_context, expected_data_req)
        controller.tk.abort.assert_called_once_with(403, 'Unauthorized to list Data Requests')
        self.assertEquals(0, controller.tk.get_action.call_count)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    def test_index_invalid_page(self):
        _patch_GET({'page': '2a'})

        # Call the function
        result = controller.index()

        # Assertions
        controller.tk.abort.assert_called_once_with(400, '"page" parameter must be an integer')
        self.assertEquals(0, controller.tk.check_access.call_count)
        self.assertEquals(0, controller.tk.get_action.call_count)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    @parameterized.expand([
        (INDEX_FUNCTION, '1', 'conwet', '', 0,    10),
        (INDEX_FUNCTION, '2', 'conwet', '', 10,   10),
        (INDEX_FUNCTION, '7', 'conwet', '', 60,   10),
        (INDEX_FUNCTION, '1', 'conwet', '', 0,    25, 25),
        (INDEX_FUNCTION, '2', 'conwet', '', 25,   25, 25),
        (INDEX_FUNCTION, '7', 'conwet', '', 150,  25, 25),
        (INDEX_FUNCTION, '5', None,     '', 40,   10),
        (INDEX_FUNCTION, '1', None,     '', 0,    10, 10, 'asc'),
        (INDEX_FUNCTION, '1', None,     '', 0,    10, 10, 'desc'),
        (INDEX_FUNCTION, '1', None,     '', 0,    10, 10, 'invalid'),
        (INDEX_FUNCTION, '1', None,     '', 0,    10, 10, None,   'free-text'),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '1', 'conwet', '',     0,    10),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '2', 'conwet', '',     10,   10),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '7', 'conwet', '',     60,   10),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '1', 'conwet', '',     0,    25, 25),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '2', 'conwet', '',     25,   25, 25),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '7', 'conwet', '',     150,  25, 25),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '1', 'conwet', '',     0,    10, 10, 'asc'),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '1', 'conwet', '',     0,    10, 10, 'desc'),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '1', 'conwet', '',     0,    10, 10, 'invalid', ''),
        (ORGANIZATION_DATAREQUESTS_FUNCTION, '1', 'conwet', '',     0,    10, 10, None,      'free-text'),
        (USER_DATAREQUESTS_FUNCTION,         '1', 'conwet', 'ckan', 0,    10),
        (USER_DATAREQUESTS_FUNCTION,         '1', '',       'ckan', 0,    10),
        (USER_DATAREQUESTS_FUNCTION,         '7', 'conwet', 'ckan', 60,   10),
        (USER_DATAREQUESTS_FUNCTION,         '7', '',       'ckan', 150,  25, 25),
        (USER_DATAREQUESTS_FUNCTION,         '1', '',       'ckan', 0,    10, 10, 'asc'),
        (USER_DATAREQUESTS_FUNCTION,         '1', '',       'ckan', 0,    10, 10, 'desc'),
        (USER_DATAREQUESTS_FUNCTION,         '1', '',       'ckan', 0,    10, 10, 'invalid'),
        (USER_DATAREQUESTS_FUNCTION,         '1', '',       'ckan', 0,    10, 10, None,      'free-text'),
    ])
    def test_index_organization_user_dr(self, func, page, organization, user, expected_offset,
                                        expected_limit, datarequests_per_page=10, sort=None,
                                        query=None):
        params = {}
        user_show_action = 'user_show'
        organization_show_action = 'organization_show'
        base_url = 'http://someurl.com/somepath/otherpath'
        expected_sort = sort if sort and sort in ['asc', 'desc'] else 'desc'

        # Expected data_dict
        expected_data_dict = {
            'offset': expected_offset,
            'limit': expected_limit,
            'sort': expected_sort
        }

        if query:
            expected_data_dict['q'] = query

        # Set datarequests_per_page
        constants.DATAREQUESTS_PER_PAGE = datarequests_per_page

        # Get parameters
        _patch_GET({})

        # Set page
        if page:
            request_helpers.request.GET['page'] = page

        # Set the organization in the correct place depending on the function
        if func == ORGANIZATION_DATAREQUESTS_FUNCTION:
            params['id'] = organization
            expected_data_dict['organization_id'] = organization
        else:
            if func == USER_DATAREQUESTS_FUNCTION:
                params['id'] = user
                expected_data_dict['user_id'] = user

            if organization:
                request_helpers.request.GET['organization'] = organization
                expected_data_dict['organization_id'] = organization

        if sort:
            request_helpers.request.GET['sort'] = sort

        if query:
            request_helpers.request.GET['q'] = query

        # Mocking
        user_show = MagicMock()
        organization_show = MagicMock()
        list_datarequests = MagicMock()

        def _get_action(action):
            if action == organization_show_action:
                return organization_show
            elif action == 'user_show':
                return user_show
            else:
                return list_datarequests

        controller.tk.get_action.side_effect = _get_action
        controller.tk.url_for.return_value = base_url

        # Call the function
        function = getattr(controller, func)
        result = function(**params)

        # Assertions
        controller.tk.check_access.assert_called_once_with(constants.LIST_DATAREQUESTS,
                                                           self.expected_context,
                                                           expected_data_dict)

        # Specific assertions depending on the function called
        if func == INDEX_FUNCTION:
            controller.tk.get_action.assert_called_once_with(constants.LIST_DATAREQUESTS)
            self.assertEquals(0, organization_show.call_count)
            expected_render_page = 'datarequests/index.html'
        elif func == ORGANIZATION_DATAREQUESTS_FUNCTION:
            self.assertEquals(2, controller.tk.get_action.call_count)
            controller.tk.get_action.assert_any_call(constants.LIST_DATAREQUESTS)
            controller.tk.get_action.assert_any_call(organization_show_action)
            self.assertEquals(organization_show.return_value, controller.c.group_dict)
            organization_show.assert_called_once_with(self.expected_context, {'id': organization})
            expected_render_page = 'organization/datarequests.html'
        elif func == USER_DATAREQUESTS_FUNCTION:
            self.assertEquals(2, controller.tk.get_action.call_count)
            controller.tk.get_action.assert_any_call(constants.LIST_DATAREQUESTS)
            controller.tk.get_action.assert_any_call(user_show_action)
            self.assertEquals(user_show.return_value, controller.c.user_dict)
            user_show.assert_called_once_with(self.expected_context, {'id': user, 'include_num_followers': True})
            expected_render_page = 'user/datarequests.html'

        # Check the values put in c
        list_datarequests.assert_called_once_with(self.expected_context, expected_data_dict)
        expected_response = list_datarequests.return_value
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
        query_param = 'q={0}&'.format(query) if query else ''
        self.assertEquals("%s?%ssort=%s&page=%d" % (base_url, query_param, expected_sort, silly_page),
                          page_arguments['url'](q=query, page=silly_page))

        # When URL function is called, tk.url_for is called to get the final URL
        if func == INDEX_FUNCTION:
            controller.tk.url_for.assert_called_once_with(
                'datarequest.index')
        elif func == ORGANIZATION_DATAREQUESTS_FUNCTION:
            controller.tk.url_for.assert_called_once_with(
                'datarequest.organization', id=organization)
        elif func == USER_DATAREQUESTS_FUNCTION:
            controller.tk.url_for.assert_called_once_with(
                'datarequest.user', id=user)

        # Check the facets
        expected_facet_titles = {}
        expected_facet_titles['state'] = controller.tk._('State')
        if func != ORGANIZATION_DATAREQUESTS_FUNCTION:
            expected_facet_titles['organization'] = controller.tk._('Organizations')

        self.assertEquals(expected_facet_titles, controller.c.facet_titles)

        # Check that the render functions has been called with the suitable parameters
        expected_user = controller.c.user_dict if hasattr(controller.c, 'user_dict') else None
        self.assertEquals(controller.tk.render.return_value, result)
        controller.tk.render.assert_called_once_with(expected_render_page, extra_vars={'user_dict': expected_user, 'group_type': 'organization'})

    ######################################################################
    ############################### DELETE ###############################
    ######################################################################

    def test_delete_not_authorized(self):
        self._test_not_authorized(controller.delete, 'delete', constants.DELETE_DATAREQUEST)

    def test_delete_not_found(self):
        self._test_not_found(controller.delete, constants.DELETE_DATAREQUEST)

    def test_delete(self):
        datarequest_id = 'example_uuidv4'
        datarequest = {
            'id': datarequest_id,
            'title': 'DR Title',
            'organization_id': 'example_uuidv4_organization'
        }

        delete_datarequest = controller.tk.get_action.return_value
        delete_datarequest.return_value = datarequest

        # Call the function
        result = controller.delete(datarequest_id)

        # Assertions
        # The result
        self.assertIsNotNone(result)

        # Functions has been called
        expected_data_dict = {'id': datarequest_id}
        controller.tk.check_access.assert_called_once_with(constants.DELETE_DATAREQUEST, self.expected_context, expected_data_dict)
        delete_datarequest.assert_called_once_with(self.expected_context, expected_data_dict)
        controller.h.flash_notice.assert_called_once_with(controller.tk._(
            'Data Request %s has been deleted' % datarequest.get('title')))

        # Redirection
        controller.tk.url_for.assert_called_once_with(
            'datarequest.index')
        controller.tk.redirect_to.assert_called_once_with(controller.tk.url_for.return_value)

    ######################################################################
    ################################ CLOSE ###############################
    ######################################################################

    def test_close_not_authorized(self):
        self._test_not_authorized(controller.close, 'close', constants.CLOSE_DATAREQUEST)

    def test_close_not_found(self):
        self._test_not_found(controller.close, constants.CLOSE_DATAREQUEST)

    @parameterized.expand([
        (None,),
        ('organization_uuidv4',)
    ])
    def test_close_datarequest(self, organization):
        self._test_close(organization)

    def _test_close(self, organization, post_content=None, errors=None, errors_summary=None, close_datarequest=None):
        controller.tk.response.location = None
        controller.tk.response.status_int = 200
        _patch_POST(post_content or {})
        errors = errors or {}
        errors_summary = errors_summary or {}
        if not close_datarequest:
            close_datarequest = MagicMock()

        datarequest_id = 'example_uuidv4'
        datarequest = {'id': 'uuid4', 'user_id': 'user_uuid4', 'title': 'example_title'}
        if organization:
            datarequest['organization_id'] = organization

        show_datarequest = MagicMock(return_value=datarequest)
        packages = [{'name': 'pack1', 'title': 'pack1'}, {'name': 'pack2', 'title': 'pack2'}]
        package_search = MagicMock(return_value={'results': packages})

        def _get_action(action):
            if action == 'package_search':
                return package_search
            elif action == constants.SHOW_DATAREQUEST:
                return show_datarequest
            elif action == constants.CLOSE_DATAREQUEST:
                return close_datarequest

        controller.tk.get_action.side_effect = _get_action

        # Call the function
        result = controller.close(datarequest_id)

        # Check that the methods has been called
        controller.tk.check_access.assert_called_once_with(constants.CLOSE_DATAREQUEST, self.expected_context, {'id': datarequest_id})
        show_datarequest.assert_called_once_with(self.expected_context, {'id': datarequest_id})

        if organization:
            package_search.assert_called_once_with({'ignore_auth': True}, {'q': 'owner_org:' + organization, 'rows': 500})
        else:
            package_search.assert_called_once_with({'ignore_auth': True}, {'rows': 500})

        # Assertions
        expected_datasets = packages
        controller.tk.render.assert_called_once_with('datarequests/close.html')
        self.assertEquals(result, controller.tk.render.return_value)

        self.assertIsNone(controller.tk.response.location)
        self.assertEquals(200, controller.tk.response.status_int)
        self.assertEquals(errors, controller.c.errors)
        self.assertEquals(errors_summary, controller.c.errors_summary)
        self.assertEquals(datarequest, controller.c.datarequest)

        self.assertEquals(expected_datasets, controller.c.datasets)

    def test_close_post_no_error(self):
        _patch_POST({'accepted_dataset': 'example_ds'})

        datarequest_id = 'example_uuidv4'
        datarequest = {'id': 'uuid4', 'user_id': 'user_uuid4', 'title': 'example_title'}
        show_datarequest = MagicMock(return_value=datarequest)
        close_datarequest = MagicMock(return_value=datarequest)

        def _get_action(action):
            if action == constants.SHOW_DATAREQUEST:
                return show_datarequest
            elif action == constants.CLOSE_DATAREQUEST:
                return close_datarequest

        controller.tk.get_action.side_effect = _get_action

        # Call the function
        result = controller.close(datarequest_id)

        # Checks
        controller.tk.url_for.assert_called_once_with(
            'datarequest.show', id=datarequest_id)
        controller.tk.redirect_to.assert_called_once_with(controller.tk.url_for.return_value)
        self.assertIsNotNone(result)

    @parameterized.expand([
        (None,),
        ('organization_uuidv4', )
    ])
    def test_close_post_errors(self, organization):
        post_content = {'accepted_dataset': 'example_ds'}
        exception = controller.tk.ValidationError({'Accepted Dataset': ['error1', 'error2']})
        close_datarequest = MagicMock(side_effect=exception)

        # Execute the test
        self._test_close(organization, post_content, exception.error_dict,
                         {'Accepted Dataset': 'error1, error2'}, close_datarequest)

    ######################################################################
    ############################### COMMENT ##############################
    ######################################################################

    def test_comment_list_not_authorized(self):
        datarequest_id = 'example_uuidv4'
        controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Call the function
        result = controller.comment(datarequest_id)

        # Assertions
        controller.tk.check_access.assert_called_once_with(constants.LIST_DATAREQUEST_COMMENTS, self.expected_context, {'datarequest_id': datarequest_id})
        controller.tk.abort.assert_called_once_with(403, 'You are not authorized to list the comments of the Data Request %s' % datarequest_id)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    def test_comment_list_not_found(self):
        datarequest_id = 'example_uuidv4'
        controller.tk.get_action.return_value.side_effect = controller.tk.ObjectNotFound('Comment not found')

        # Call the function
        result = controller.comment(datarequest_id)

        # Assertions
        controller.tk.get_action(constants.COMMENT_DATAREQUEST)
        controller.tk.abort.assert_called_once_with(404, 'Data Request %s not found' % datarequest_id)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    @parameterized.expand([
        (),
        (True,  False),
        (False, True),
        (True,  False, controller.tk.NotAuthorized),
        (False, True,  controller.tk.NotAuthorized),
        (True,  False, controller.tk.ObjectNotFound('Exception')),
        (False, True,  controller.tk.ObjectNotFound('Exception')),
        (True,  False, controller.tk.ValidationError({'comment': ['error1', 'error2']})),
        (False, True, controller.tk.ValidationError({'comment': ['error1', 'error2']}))

    ])
    def test_comment_list(self, new_comment=False, update_comment=False,
                          comment_or_update_exception=None):

        _patch_POST({})
        datarequest_id = 'example_uuidv4'
        comment_id = 'comment_uuidv4'
        comment = 'example comment'
        new_comment_id = 'another_uuidv4'

        if new_comment or update_comment:
            _patch_POST({
                'datarequest_id': datarequest_id,
                'comment': comment,
                'comment-id': comment_id if update_comment else ''
            })

        datarequest = {'id': 'uuid4', 'user_id': 'user_uuid4', 'title': 'example_title'}
        comments_list = [
            {'comment': 'Comment 1\nwith new line'},
            {'comment': 'Comment 2\nwith two\nnew lines'},
            {'comment': 'Comment 3 with link https://fiware.org/some/path?param1=1&param2=2'},
            {'comment': 'Comment 4 with two links https://fiware.org/some/path?param1=1&param2=2 and https://google.es'},
            {'comment': 'Comment\nwith http://fiware.org\nhttp://fiware.eu'}
        ]

        default_action_return = {
            'id': new_comment_id if new_comment else comment_id,
            'comment': comment
        }

        show_datarequest = MagicMock(return_value=datarequest)
        list_datarequest_comments = MagicMock(return_value=comments_list)
        default_action = MagicMock(side_effect=comment_or_update_exception, return_value=default_action_return)

        def _get_action(action):
            if action == constants.SHOW_DATAREQUEST:
                return show_datarequest
            elif action == constants.LIST_DATAREQUEST_COMMENTS:
                return list_datarequest_comments
            else:
                return default_action

        delattr(controller.c, 'updated_comment')
        delattr(controller.c, 'errors')
        controller.tk.get_action.side_effect = _get_action

        # Call the function
        result = controller.comment(datarequest_id)

        if comment_or_update_exception == controller.tk.NotAuthorized:
            action = 'comment' if new_comment else 'update comment'
            controller.tk.abort.assert_called_once_with(403, 'You are not authorized to %s' % action)
            self.assertEquals(result, 'aborted')

        elif type(comment_or_update_exception) == controller.tk.ObjectNotFound:
            controller.tk.abort.assert_called_once_with(404, str(comment_or_update_exception))
            self.assertEquals(result, 'aborted')

        else:
            if type(comment_or_update_exception) == controller.tk.ValidationError:
                # Abort never called
                self.assertEquals(0, controller.tk.abort.call_count)

                # Check controller.c values
                self.assertEquals(comment_or_update_exception.error_dict, controller.c.errors)

                errors_summary = {
                    key: ', '.join(error)
                    for key, error in comment_or_update_exception.error_dict.items()}

                self.assertEquals(errors_summary, controller.c.errors_summary)

            # Check the result
            self.assertEquals(result, controller.tk.render.return_value)
            controller.tk.render.assert_called_once_with('datarequests/comment.html')

            # Verify comments and data request
            self.assertEquals(controller.c.datarequest, datarequest)
            self.assertEquals(controller.c.comments, comments_list)

            # Check calls
            show_datarequest.assert_called_once_with(self.expected_context, {'id': datarequest_id})
            list_datarequest_comments.assert_called_once_with(self.expected_context, {'datarequest_id': datarequest_id})

            if new_comment:
                controller.tk.get_action.assert_any_call(constants.COMMENT_DATAREQUEST)
            elif update_comment:
                controller.tk.get_action.assert_any_call(constants.UPDATE_DATAREQUEST_COMMENT)

            if new_comment or update_comment:
                default_action.assert_called_once_with(
                    self.expected_context, {
                        'datarequest_id': datarequest_id,
                        'comment': comment, 'id': comment_id if update_comment else ''
                    })

                # self.assertEquals(comment, controller.c.updated_comment.comment['comment'])

                updated_comment_id = controller.c.updated_comment['comment']['id']
                if new_comment:
                    if comment_or_update_exception:
                        self.assertEquals('', updated_comment_id)
                    else:
                        self.assertEquals(new_comment_id, updated_comment_id)

                if update_comment:
                    self.assertEquals(comment_id, updated_comment_id)

    ######################################################################
    ########################### DELETE COMMENT ###########################
    ######################################################################

    def test_delete_comment_not_authorized(self):
        comment_id = 'example_uuidv4_comment'
        controller.tk.check_access.side_effect = controller.tk.NotAuthorized('User not authorized')

        # Call the function
        result = controller.delete_comment('datarequest_id', comment_id)

        # Assertions
        controller.tk.check_access.assert_called_once_with(constants.DELETE_DATAREQUEST_COMMENT,
                                                           self.expected_context, {'id': comment_id})
        controller.tk.abort.assert_called_once_with(403, 'You are not authorized to delete this comment')
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    def test_delete_comment_not_found(self):
        datarequest_id = 'example_uuidv4'
        comment_id = 'comment_uuidv4'
        controller.tk.get_action.return_value.side_effect = controller.tk.ObjectNotFound('Comment not found')

        # Call the function
        result = controller.delete_comment(datarequest_id, comment_id)

        # Assertions
        controller.tk.get_action(constants.DELETE_DATAREQUEST_COMMENT)
        controller.tk.abort.assert_called_once_with(404, 'Comment %s not found' % comment_id)
        self.assertEquals(0, controller.tk.render.call_count)
        self.assertEquals(result, 'aborted')

    def test_delete_comment(self):
        datarequest_id = 'example_uuidv4'
        comment_id = 'comment_uuidv4'

        # Call
        controller.delete_comment(datarequest_id, comment_id)

        # Check calls
        controller.tk.get_action.assert_called_once_with(constants.DELETE_DATAREQUEST_COMMENT)
        delete_datarequest_comment = controller.tk.get_action.return_value
        delete_datarequest_comment.assert_called_once_with(self.expected_context, {'id': comment_id})

        # Check redirection
        controller.tk.url_for.assert_called_once_with(
            'datarequest.comment', id=datarequest_id)
        controller.tk.redirect_to.assert_called_once_with(controller.tk.url_for.return_value)

    ######################################################################
    ########################## FOLLOW/UNFOLLOW ###########################
    ######################################################################

    def test_follow(self):
        controller.follow('example_uuidv4')

    def test_unfollow(self):
        controller.unfollow('example_uuidv4')
