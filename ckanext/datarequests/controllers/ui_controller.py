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

import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as plugins
import ckanext.datarequests.constants as constants

from ckan.common import request

tk = plugins.toolkit
c = tk.c


class DataRequestsUI(base.BaseController):

    def index(self):
        return tk.render('datarequests/index.html')

    def _process_post(self, action, context):
        # If the user has submitted the form, the data request must be created
        if request.POST:
            data_dict = {}
            data_dict['title'] = request.POST.get('title', '')
            data_dict['description'] = request.POST.get('description', '')
            data_dict['organization_id'] = request.POST.get('organization_id', '')

            if action == constants.DATAREQUEST_UPDATE:
                data_dict['id'] = request.POST.get('id', '')

            try:
                result = tk.get_action(action)(context, data_dict)
                tk.response.status_int = 302
                tk.response.location = '%s/%s' % (constants.DATAREQUESTS_MAIN_PATH,
                                                  result['id'])

            except tk.ValidationError as e:
                # Fill the fields that will display some information in the page
                c.datarequest = {
                    'id': data_dict.get('id', ''),
                    'title': data_dict.get('title', ''),
                    'description': data_dict.get('description', ''),
                    'organization_id': data_dict.get('organization_id', '')
                }
                c.errors = e.error_dict
                c.errors_summary = {}

                for key, error in c.errors.items():
                    c.errors_summary[key] = ', '.join(error)

    def new(self):

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        # Basic intialization
        c.datarequest = {}
        c.errors = None
        c.errors_summary = None

        # Check access
        try:
            tk.check_access(constants.DATAREQUEST_CREATE, context, None)
            self._process_post(constants.DATAREQUEST_CREATE, context)

            # The form is always rendered
            return tk.render('datarequests/new.html')

        except tk.NotAuthorized:
            tk.abort(401, tk._('Unauthorized to create a Data Request'))

    def show(self, id):
        data_dict = {'id': id}
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        try:
            tk.check_access(constants.DATAREQUEST_SHOW, context, data_dict)
            c.datarequest = tk.get_action(constants.DATAREQUEST_SHOW)(context, data_dict)
            
            try:
                c.datarequest['user'] = tk.get_action('user_show')(context, {'id': c.datarequest['user_id']})
            except tk.ObjectNotFound:
                pass

            if c.datarequest['organization_id']:
                try:
                    organization_show = tk.get_action('organization_show')
                    c.datarequest['organization'] = organization_show(context, {'id': c.datarequest['organization_id']})
                except tk.ObjectNotFound:
                    pass

            return tk.render('datarequests/show.html')
        except tk.ObjectNotFound:
            tk.abort(404, tk._('Data Request %s not found') % id)
        except tk.NotAuthorized:
            tk.abort(401, tk._('You are not authorized to view the Data Request %s'
                               % id))

    def update(self, id):
        data_dict = {'id': id}
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        try:
            tk.check_access(constants.DATAREQUEST_UPDATE, context, data_dict)
            c.datarequest = tk.get_action(constants.DATAREQUEST_SHOW)(context, data_dict)
            c.original_title = c.datarequest.get('title')
            self._process_post(constants.DATAREQUEST_UPDATE, context)
            return tk.render('datarequests/edit.html')
        except tk.ObjectNotFound:
            tk.abort(404, tk._('Data Request %s not found') % id)
        except tk.NotAuthorized:
            tk.abort(401, tk._('You are not authorized to update the Data Request %s'
                               % id))
