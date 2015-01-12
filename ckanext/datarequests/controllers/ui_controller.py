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

    def new(self):

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        # Basic intialization
        c.datarequest = None
        c.errors = None
        c.errors_summary = None

        # Check access
        try:
            tk.check_access(constants.DATAREQUEST_CREATE, context, None)

            # If the user has submitted the form, the data request must be created
            if request.POST:
                request_data = {}
                request_data['title'] = request.POST.get('title', '')
                request_data['description'] = request.POST.get('description', '')
                request_data['organization'] = request.POST.get('organization', '')

                try:
                    tk.get_action(constants.DATAREQUEST_CREATE)(context, request_data)
                except tk.ValidationError as e:
                    # Fill the fields that will display some information in the page
                    c.datarequest = {
                        'title': request_data['title'],
                        'description': request_data['description'],
                        'organization': request_data['organization']
                    }
                    c.errors = e.error_dict
                    c.errors_summary = {}

                    for key, error in c.errors.items():
                        c.errors_summary[key] = ', '.join(error)

            # The form is always rendered
            return tk.render('datarequests/new.html')

        except tk.NotAuthorized:
            tk.abort(401, tk._('Unauthorized to create a Data Request'))
