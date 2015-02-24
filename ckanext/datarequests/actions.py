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


def _dictize_datarequest(datarequest):
    # Transform time
    open_time = str(datarequest.open_time)
    # Close time can be None and the transformation is only needed when the
    # fields contains a valid date
    close_time = datarequest.close_time
    close_time = str(close_time) if close_time else close_time

    # Convert the data request into a dict
    datarequest = {
        'id': datarequest.id,
        'user_id': datarequest.user_id,
        'title': datarequest.title,
        'description': datarequest.description,
        'organization_id': datarequest.organization_id,
        'open_time': open_time,
        'accepted_dataset': datarequest.accepted_dataset,
        'close_time': close_time,
        'closed': datarequest.closed
    }

    return datarequest


def _undictize_datarequest_basic(data_request, data_dict):
    data_request.title = data_dict['title']
    data_request.description = data_dict['description']
    organization = data_dict['organization_id']
    data_request.organization_id = organization if organization else None


def datarequest_create(context, data_dict):
    '''
    Action to create a new dara request. The function checks the access rights
    of the user before creating the data request. If the user is not allowed
    a NotAuthorized exception will be risen

    In addition, you should note that the parameters will be checked and an
    exception (ValidationError) will be risen if some of these parameters are
    not valid

    :param title: The title of the data request
    :type title: string

    :param description: A brief description for your data request
    :type description: string

    :param organiztion_id: If you want to create the data request in a specific
        organization.
    :type organization_id: string

    :returns: A dict with the data request (id, user_id, title, description, 
        organization_id, open_time, accepted_dataset, close_time, closed)
    :rtype: dict
    '''

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
    _undictize_datarequest_basic(data_req, data_dict)
    data_req.user_id = context['auth_user_obj'].id
    data_req.open_time = datetime.datetime.now()

    session.add(data_req)
    session.commit()

    return _dictize_datarequest(data_req)


def datarequest_show(context, data_dict):
    '''
    Action to retrieve the information of a data request. The only required
    parameter is the id of the data request. A NotFound exception will be
    risen if the id is not found. 

    Access rights will be checked before returning the information and an
    exception will be risen (NotAuthorized) if the user is not authorized

    :param id: The id of the data request to be shown
    :type id: string

    :returns: A dict with the data request (id, user_id, title, description, 
        organization_id, open_time, accepted_dataset, close_time, closed)
    :rtype: dict
    '''

    model = context['model']
    datarequest_id = data_dict.get('id', '')

    if not datarequest_id:
        raise tk.ValidationError('Data Request ID has not been included')

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_SHOW, context, data_dict)

    # Get the data request
    result = db.DataRequest.get(id=datarequest_id)
    if not result:
        raise tk.ObjectNotFound('Data Request %s not found in the data base' % datarequest_id)

    data_req = result[0]
    return _dictize_datarequest(data_req)


def datarequest_update(context, data_dict):
    '''
    Action to update a new dara request. The function checks the access rights
    of the user before updating the data request. If the user is not allowed
    a NotAuthorized exception will be risen

    In addition, you should note that the parameters will be checked and an
    exception (ValidationError) will be risen if some of these parameters are
    not valid

    :param id: The id of the data request to be updated
    :type id: string

    :param title: The title of the data request
    :type title: string

    :param description: A brief description for your data request
    :type description: string

    :param organiztion_id: If you want to create the data request in a specific
        organization.
    :type organization_id: string

    :returns: A dict with the data request (id, user_id, title, description, 
        organization_id, open_time, accepted_dataset, close_time, closed)
    :rtype: dict
    '''

    model = context['model']
    session = context['session']
    datarequest_id = data_dict.get('id', '')

    if not datarequest_id:
        raise tk.ValidationError('Data Request ID has not been included')

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_UPDATE, context, data_dict)

    # Get the initial data
    result = db.DataRequest.get(id=datarequest_id)
    if not result:
        raise tk.ObjectNotFound('Data Request %s not found in the data base' % datarequest_id)

    data_req = result[0]

    # Avoid the validator to return an error when the user does not change the title
    context['avoid_existing_title_check'] = data_req.title == data_dict['title']

    # Validate data
    validator.validate_datarequest(context, data_dict)

    # Set the data provided by the user in the data_red
    _undictize_datarequest_basic(data_req, data_dict)

    session.add(data_req)
    session.commit()

    return _dictize_datarequest(data_req)


def datarequest_index(context, data_dict):
    '''
    Returns a list with the existing data requests. Rights access will be checked
    before returning the results. If the user is not allowed, a NotAuthorized 
    exception will be risen

    :parameter organization_id: This parameter is optional and allows users
        to filter the results by organization
    :type organization_id: string

    :parameter closed: This parameter is optional and allos users to filter
        the result by the data request status (open or closed)
    :type closed: bool

    :parameter offset: The first element to be returned (0 by default)
    :type offset: int

    :parameter limit: The max number of data requests to be returned (10 by default)
    :type limit: init

    :returns: A dict with three fields: result (a list of data requests),
        facets (a list of the facets that can be used) and count (the total 
        number of existing data requests)
    :rtype: dict
    '''

    model = context['model']
    organization_show = tk.get_action('organization_show')

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_INDEX, context, data_dict)

    # Get the organization
    organization_id = data_dict.get('organization_id', None)
    params = {}
    if organization_id:
        # Get organization ID (in some cases, user give the system the organization name)
        organization_id = organization_show({'ignore_auth': True}, {'id': organization_id}).get('id')

        # Include the organization into the parameters to filter the database query
        params['organization_id'] = organization_id

    # Filter by state
    closed = data_dict.get('closed', None)
    if closed is not None:
        params['closed'] = closed

    # Call the function
    db_datarequests = db.DataRequest.get_ordered_by_date(**params)

    # Dictize the results
    offset = data_dict.get('offset', 0)
    limit = data_dict.get('limit', constants.DATAREQUESTS_PER_PAGE)
    datarequests = []
    for data_req in db_datarequests[offset:offset + limit]:
        datarequests.append(_dictize_datarequest(data_req))

    # Facets
    no_processed_organization_facet = {}
    CLOSED = 'Closed'
    OPEN = 'Open'
    no_processed_state_facet = {CLOSED:0 , OPEN: 0}
    for data_req in db_datarequests:
        if data_req.organization_id:
            # Facets
            if data_req.organization_id in no_processed_organization_facet:
                no_processed_organization_facet[data_req.organization_id] += 1
            else:
                no_processed_organization_facet[data_req.organization_id] = 1

        no_processed_state_facet[CLOSED if data_req.closed else OPEN] +=1

    # Format facets
    organization_facet = []
    for organization_id in no_processed_organization_facet:
        try:
            organization = organization_show({'ignore_auth': True}, {'id': organization_id})
            organization_facet.append({
                'name': organization.get('name'),
                'display_name': organization.get('display_name'),
                'count': no_processed_organization_facet[organization_id]
            })
        except:
            pass

    state_facet = []
    for state in no_processed_state_facet:
        if no_processed_state_facet[state]:
            state_facet.append({
                'name': state.lower(),
                'display_name': state,
                'count': no_processed_state_facet[state]
            })

    result = {
        'count': len(db_datarequests),
        'facets': {},
        'result': datarequests
    }

    # Facets can only be included if they contain something
    if organization_facet:
        result['facets']['organization'] = {'items': organization_facet}

    if state_facet:
        result['facets']['state'] = {'items': state_facet}

    return result

def datarequest_delete(context, data_dict): 
    '''
    Action to delete a new dara request. The function checks the access rights
    of the user before deleting the data request. If the user is not allowed
    a NotAuthorized exception will be risen

    :param id: The id of the data request to be updated
    :type id: string

    :returns: A dict with the data request (id, user_id, title, description, 
        organization_id, open_time, accepted_dataset, close_time, closed)
    :rtype: dict
    '''

    model = context['model']
    session = context['session']
    datarequest_id = data_dict.get('id', '')

    # Check id
    if not datarequest_id:
        raise tk.ValidationError('Data Request ID has not been included')

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_DELETE, context, data_dict)

    # Get the data request
    result = db.DataRequest.get(id=datarequest_id)
    if not result:
        raise tk.ObjectNotFound('Data Request %s not found in the data base' % datarequest_id)

    data_req = result[0]
    session.delete(data_req)
    session.commit()

    return _dictize_datarequest(data_req)

def datarequest_close(context, data_dict):
    '''
    Action to close a data request. Access rights will be checked before closing the
    data request. If the user is not allowed, a NotAuthorized exception will be risen

    :param id: The id of the data request to be closed
    :type id: string

    :parameter accepted_dataset: The ID of the dataset accepted as solution for this
        data request
    :type accepted_dataset: string
    '''

    model = context['model']
    session = context['session']
    datarequest_id = data_dict.get('id', '')

    # Check id
    if not datarequest_id:
        raise tk.ValidationError('Data Request ID has not been included')

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_CLOSE, context, data_dict)

    # Get the data request
    result = db.DataRequest.get(id=datarequest_id)
    if not result:
        raise tk.ObjectNotFound('Data Request %s not found in the data base' % datarequest_id)

    # Validate data
    validator.validate_datarequest_closing(context, data_dict)

    data_req = result[0]
    data_req.closed = True
    data_req.accepted_dataset = data_dict.get('accepted_dataset', '')
    data_req.close_time = datetime.datetime.now()

    session.add(data_req)
    session.commit()
