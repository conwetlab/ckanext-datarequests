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


import ckan.plugins as plugins
import constants
import datetime
import db
import validator

c = plugins.toolkit.c
tk = plugins.toolkit


def datarequest_create(context, request_data):

    model = context['model']
    session = context['session']

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_CREATE, context, request_data)

    # Validate data
    validator.validate_datarequest(context, request_data)

    # Store the data
    data_req = db.DataRequest()
    data_req.user_id = context['auth_user_obj'].id
    data_req.title = request_data['title']
    data_req.description = request_data['description']
    data_req.organization = request_data['organization']
    data_req.open_time = datetime.datetime.now()

    session.add(data_req)
    session.commit()
