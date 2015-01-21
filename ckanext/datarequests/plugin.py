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

import ckan.plugins as p
import ckan.plugins.toolkit as tk
import auth
import actions
import constants


class DataRequestsPlugin(p.SingletonPlugin):

    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)

    ######################################################################
    ############################## IACTIONS ##############################
    ######################################################################

    def get_actions(self):
        return {
            constants.DATAREQUEST_CREATE: actions.datarequest_create,
            constants.DATAREQUEST_SHOW: actions.datarequest_show,
            constants.DATAREQUEST_UPDATE: actions.datarequest_update,
            constants.DATAREQUEST_INDEX: actions.datarequest_index
        }

    ######################################################################
    ########################### AUTH FUNCTIONS ###########################
    ######################################################################

    def get_auth_functions(self):
        return {
            constants.DATAREQUEST_CREATE: auth.datarequest_create,
            constants.DATAREQUEST_SHOW: auth.datarequest_show,
            constants.DATAREQUEST_UPDATE: auth.datarequest_update,
            constants.DATAREQUEST_INDEX: auth.datarequest_index
        }

    ######################################################################
    ############################ ICONFIGURER #############################
    ######################################################################

    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

        # Register this plugin's fanstatic directory with CKAN.
        tk.add_public_directory(config, 'public')

    ######################################################################
    ############################## IROUTES ###############################
    ######################################################################

    def before_map(self, m):
        # Data Requests index
        m.connect('datarequests_index', constants.DATAREQUESTS_MAIN_PATH,
                  controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                  action='index', conditions=dict(method=['GET']))

        # Create Data Request
        m.connect('%s/new' % constants.DATAREQUESTS_MAIN_PATH,
                  controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                  action='new', conditions=dict(method=['GET', 'POST']))

        # Show Data Request
        m.connect('datarequest_show', '%s/{id}' % constants.DATAREQUESTS_MAIN_PATH,
                  controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                  action='show', conditions=dict(method=['GET']), ckan_icon='question-sign')

        # Update Data Request
        m.connect('%s/edit/{id}' % constants.DATAREQUESTS_MAIN_PATH,
                  controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                  action='update', conditions=dict(method=['GET', 'POST']))

        # Data Request that belongs to an organization
        m.connect('organization_datarequests', '/organization%s/{id}' % constants.DATAREQUESTS_MAIN_PATH,
                  controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                  action='organization_datarequests', conditions=dict(method=['GET']), 
                  ckan_icon='question-sign')

        return m
