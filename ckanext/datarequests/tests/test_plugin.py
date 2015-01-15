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

from mock import MagicMock


class DataRequestPlutinTest(unittest.TestCase):

    def setUp(self):
        self._actions = plugin.actions
        plugin.actions = MagicMock()

        self._auth = plugin.auth
        plugin.auth = MagicMock()

        self._tk = plugin.tk
        plugin.tk = MagicMock()

        # plg = plugin
        self.plg_instance = plugin.DataRequestsPlugin()
        self.datarequest_create = constants.DATAREQUEST_CREATE
        self.datarequest_show = constants.DATAREQUEST_SHOW
        self.datarequest_update = constants.DATAREQUEST_UPDATE

    def tearDown(self):
        plugin.actions = self._actions
        plugin.auth = self._auth
        plugin.tk = self._tk

    def test_get_actions(self):
        actions = self.plg_instance.get_actions()
        self.assertEquals(3, len(actions))
        self.assertEquals(plugin.actions.datarequest_create, actions[self.datarequest_create])
        self.assertEquals(plugin.actions.datarequest_show, actions[self.datarequest_show])
        self.assertEquals(plugin.actions.datarequest_update, actions[self.datarequest_update])

    def test_get_auth_functions(self):
        auth_functions = self.plg_instance.get_auth_functions()
        self.assertEquals(3, len(auth_functions))
        self.assertEquals(plugin.auth.datarequest_create, auth_functions[self.datarequest_create])
        self.assertEquals(plugin.auth.datarequest_show, auth_functions[self.datarequest_show])
        self.assertEquals(plugin.auth.datarequest_update, auth_functions[self.datarequest_update])

    def test_update_config(self):
        config = MagicMock()
        self.plg_instance.update_config(config)
        plugin.tk.add_template_directory.assert_called_once_with(config, 'templates')

    def test_before_map(self):
        mapa = MagicMock()
        dr_basic_path = '/datarequest'
        self.plg_instance.before_map(mapa)

        self.assertEquals(4, mapa.connect.call_count)
        mapa.connect.assert_any_call('datarequests_index', dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='index', conditions=dict(method=['GET']))

        mapa.connect.assert_any_call('%s/new' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='new', conditions=dict(method=['GET', 'POST']))

        mapa.connect.assert_any_call('datarequest_show', '%s/{id}' % constants.DATAREQUESTS_MAIN_PATH,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='show', conditions=dict(method=['GET']), ckan_icon='question-sign')

        mapa.connect.assert_any_call('%s/edit/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='update', conditions=dict(method=['GET', 'POST']))
