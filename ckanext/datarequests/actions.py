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


def datarequest_create(context, data_dict):

    model = context['model']
    session = context['session']

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_CREATE, context, data_dict)

    # Validate data
    validator.validate_datarequest(context, data_dict)

    # Store the data
    data_req = db.DataRequest()
    data_req.user_id = context['auth_user_obj'].id
    data_req.title = data_dict['title']
    data_req.description = data_dict['description']
    organization = data_dict['organization']
    data_req.organization = organization if organization else None
    data_req.open_time = datetime.datetime.now()

    session.add(data_req)
    session.commit()


def datarequest_show(context, data_dict):

    model = context['model']
    datarequest_id = data_dict['id']

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_SHOW, context, data_dict)

    # Get the data request
    result = db.DataRequest.get(id=datarequest_id)
    if not result:
        raise tk.ObjectNotFound('Data Request %s not found in the data base' % datarequest_id)

    dr_db = result[0]
    # Transform time
    open_time = str(dr_db.open_time)
    # Close time can be None and the transformation is only needed when the
    # fields contains a valid date
    close_time = dr_db.close_time
    close_time = str(close_time) if close_time else close_time

    # Convert the data request into a dict
    datarequest = {
        'id': dr_db.id,
        'user_id': dr_db.user_id,
        'title': dr_db.title,
        'description': dr_db.description,
        'organization': dr_db.organization,
        'open_time': open_time,
        'accepted_dataset': dr_db.accepted_dataset,
        'close_time': close_time,
        'closed': dr_db.closed
    }

    return datarequest
