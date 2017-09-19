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

import ckanext.datarequests.plugin as plugin
import ckanext.datarequests.constants as constants
import unittest

from mock import MagicMock, patch
from nose_parameterized import parameterized

TOTAL_ACTIONS = 11
COMMENTS_ACTIONS = 5
ACTIONS_NO_COMMENTS = TOTAL_ACTIONS - COMMENTS_ACTIONS


class DataRequestPluginTest(unittest.TestCase):

    def setUp(self):
        self.actions_patch = patch('ckanext.datarequests.plugin.actions')
        self.actions_mock = self.actions_patch.start()

        self.auth_patch = patch('ckanext.datarequests.plugin.auth')
        self.auth_mock = self.auth_patch.start()

        self.tk_patch = patch('ckanext.datarequests.plugin.tk')
        self.tk_mock = self.tk_patch.start()

        self.config_patch = patch('ckanext.datarequests.plugin.config')
        self.config_mock = self.config_patch.start()

        self.helpers_patch = patch('ckanext.datarequests.plugin.helpers')
        self.helpers_mock = self.helpers_patch.start()

        self.partial_patch = patch('ckanext.datarequests.plugin.partial')
        self.partial_mock = self.partial_patch.start()

        self.h_patch = patch('ckanext.datarequests.plugin.h')
        self.h_mock = self.h_patch.start()

        self.datarequest_create = constants.DATAREQUEST_CREATE
        self.datarequest_show = constants.DATAREQUEST_SHOW
        self.datarequest_update = constants.DATAREQUEST_UPDATE
        self.datarequest_index = constants.DATAREQUEST_INDEX
        self.datarequest_delete = constants.DATAREQUEST_DELETE
        self.datarequest_comment = constants.DATAREQUEST_COMMENT
        self.datarequest_comment_list = constants.DATAREQUEST_COMMENT_LIST
        self.datarequest_comment_show = constants.DATAREQUEST_COMMENT_SHOW
        self.datarequest_comment_update = constants.DATAREQUEST_COMMENT_UPDATE
        self.datarequest_comment_delete = constants.DATAREQUEST_COMMENT_DELETE

    def tearDown(self):
        self.actions_patch.stop()
        self.auth_patch.stop()
        self.tk_patch.stop()
        self.config_patch.stop()
        self.helpers_patch.stop()
        self.partial_patch.stop()
        self.h_patch.stop()

    def test_is_fontawesome_4_false_ckan_version_does_not_exist(self):
        delattr(self.h_mock, 'ckan_version')
        self.assertFalse(plugin.is_fontawesome_4())

    def test_is_fontawesome_4_false_old_ckan_version(self):
        self.h_mock.ckan_version.return_value = '2.6.0'
        self.assertFalse(plugin.is_fontawesome_4())

    def test_is_fontawesome_4_true_new_ckan_version(self):
        self.h_mock.ckan_version.return_value = '2.7.0'
        self.assertTrue(plugin.is_fontawesome_4())

    def test_get_plus_icon_new(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=True)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('plus-square', plugin.get_plus_icon())

    def test_get_plus_icon_old(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=False)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('plus-sign-alt', plugin.get_plus_icon())

    def test_get_question_icon_new(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=True)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('question-circle', plugin.get_question_icon())

    def test_get_question_icon_old(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=False)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        self.assertEquals('question-sign', plugin.get_question_icon())

    @parameterized.expand([
        ('True',),
        ('False',)
    ])
    def test_get_actions(self, comments_enabled):

        actions_len = TOTAL_ACTIONS if comments_enabled == 'True' else ACTIONS_NO_COMMENTS

        # Configure config and create instance
        plugin.config.get.return_value = comments_enabled
        self.plg_instance = plugin.DataRequestsPlugin()

        # Get actions
        actions = self.plg_instance.get_actions()

        self.assertEquals(actions_len, len(actions))
        self.assertEquals(plugin.actions.datarequest_create, actions[self.datarequest_create])
        self.assertEquals(plugin.actions.datarequest_show, actions[self.datarequest_show])
        self.assertEquals(plugin.actions.datarequest_update, actions[self.datarequest_update])
        self.assertEquals(plugin.actions.datarequest_index, actions[self.datarequest_index])
        self.assertEquals(plugin.actions.datarequest_delete, actions[self.datarequest_delete])

        if comments_enabled == 'True':
            self.assertEquals(plugin.actions.datarequest_comment, actions[self.datarequest_comment])
            self.assertEquals(plugin.actions.datarequest_comment_list, actions[self.datarequest_comment_list])
            self.assertEquals(plugin.actions.datarequest_comment_show, actions[self.datarequest_comment_show])
            self.assertEquals(plugin.actions.datarequest_comment_update, actions[self.datarequest_comment_update])
            self.assertEquals(plugin.actions.datarequest_comment_delete, actions[self.datarequest_comment_delete])

    @parameterized.expand([
        ('True',),
        ('False',)
    ])
    def test_get_auth_functions(self, comments_enabled):

        auth_functions_len = TOTAL_ACTIONS if comments_enabled == 'True' else ACTIONS_NO_COMMENTS

        # Configure config and create instance
        plugin.config.get.return_value = comments_enabled
        self.plg_instance = plugin.DataRequestsPlugin()

        # Get auth functions
        auth_functions = self.plg_instance.get_auth_functions()

        self.assertEquals(auth_functions_len, len(auth_functions))
        self.assertEquals(plugin.auth.datarequest_create, auth_functions[self.datarequest_create])
        self.assertEquals(plugin.auth.datarequest_show, auth_functions[self.datarequest_show])
        self.assertEquals(plugin.auth.datarequest_update, auth_functions[self.datarequest_update])
        self.assertEquals(plugin.auth.datarequest_index, auth_functions[self.datarequest_index])
        self.assertEquals(plugin.auth.datarequest_delete, auth_functions[self.datarequest_delete])

        if comments_enabled == 'True':
            self.assertEquals(plugin.auth.datarequest_comment, auth_functions[self.datarequest_comment])
            self.assertEquals(plugin.auth.datarequest_comment_list, auth_functions[self.datarequest_comment_list])
            self.assertEquals(plugin.auth.datarequest_comment_show, auth_functions[self.datarequest_comment_show])
            self.assertEquals(plugin.auth.datarequest_comment_update, auth_functions[self.datarequest_comment_update])
            self.assertEquals(plugin.auth.datarequest_comment_delete, auth_functions[self.datarequest_comment_delete])

    def test_update_config(self):
        # Create instance
        self.plg_instance = plugin.DataRequestsPlugin()

        # Test
        config = MagicMock()
        self.plg_instance.update_config(config)
        plugin.tk.add_template_directory.assert_called_once_with(config, 'templates')

    @parameterized.expand([
        ('True',),
        ('False')
    ])
    def test_before_map(self, comments_enabled):

        urls_set = 10
        mapa_calls = urls_set if comments_enabled == 'True' else urls_set - 2

        # Configure config and get instance
        plugin.config.get.return_value = comments_enabled
        self.plg_instance = plugin.DataRequestsPlugin()

        mock_icon = 'icon'
        get_question_icon_patch = patch('ckanext.datarequests.plugin.get_question_icon', return_value=mock_icon)
        get_question_icon_patch.start()
        self.addCleanup(get_question_icon_patch.stop)

        # Test
        mapa = MagicMock()
        dr_basic_path = 'datarequest'
        self.plg_instance.before_map(mapa)

        self.assertEquals(mapa_calls, mapa.connect.call_count)
        mapa.connect.assert_any_call('datarequests_index', "/%s" % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='index', conditions=dict(method=['GET']))

        mapa.connect.assert_any_call('/%s/new' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='new', conditions=dict(method=['GET', 'POST']))

        mapa.connect.assert_any_call('datarequest_show', '/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='show', conditions=dict(method=['GET']), ckan_icon=mock_icon)

        mapa.connect.assert_any_call('/%s/edit/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='update', conditions=dict(method=['GET', 'POST']))

        mapa.connect.assert_any_call('/%s/delete/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='delete', conditions=dict(method=['POST']))

        mapa.connect.assert_any_call('/%s/close/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='close', conditions=dict(method=['GET', 'POST']))

        mapa.connect.assert_any_call('organization_datarequests', 
            '/organization/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='organization_datarequests', conditions=dict(method=['GET']), 
            ckan_icon=mock_icon)

        mapa.connect.assert_any_call('user_datarequests',
            '/user/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='user_datarequests', conditions=dict(method=['GET']), 
            ckan_icon=mock_icon)

        if comments_enabled == 'True':
            mapa.connect.assert_any_call('datarequest_comment', '/%s/comment/{id}' % dr_basic_path,
                controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                action='comment', conditions=dict(method=['GET', 'POST']), ckan_icon='comment')

            mapa.connect.assert_any_call('/%s/comment/{datarequest_id}/delete/{comment_id}' % dr_basic_path,
                controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                action='delete_comment', conditions=dict(method=['GET', 'POST']))

    @parameterized.expand([
        ('True',  'True'),
        ('True',  'False'),
        ('False', 'True'),
        ('False', 'False')
    ])
    def test_helpers(self, comments_enabled, show_datarequests_badge):

        # Configure config and get instance
        plugin.config = {
            'ckan.datarequests.comments': comments_enabled,
            'ckan.datarequests.show_datarequests_badge': show_datarequests_badge
        }
        self.plg_instance = plugin.DataRequestsPlugin()

        # Check result
        show_comments_expected = True if comments_enabled == 'True' else False
        helpers = self.plg_instance.get_helpers()
        self.assertEquals(helpers['show_comments_tab'](), show_comments_expected)
        self.assertEquals(helpers['get_comments_number'], plugin.helpers.get_comments_number)
        self.assertEquals(helpers['get_comments_badge'], plugin.helpers.get_comments_badge)
        self.assertEquals(helpers['get_open_datarequests_number'], plugin.helpers.get_open_datarequests_number)
        self.assertEquals(helpers['get_open_datarequests_badge'], plugin.partial.return_value)

        # Check that partial has been called
        show_datarequests_expected = True if show_datarequests_badge == 'True' else False
        plugin.partial.assert_called_once_with(plugin.helpers.get_open_datarequests_badge, show_datarequests_expected)
