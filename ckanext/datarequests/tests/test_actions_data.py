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

import copy
import datetime

from mock import MagicMock

######################################################################
############################## FUNCTIONS #############################
######################################################################

def dictice_ddbb_response(datarequest):
    return {
        'id': datarequest.id,
        'user_id': datarequest.user_id,
        'title': datarequest.title,
        'description': datarequest.description,
        'organization_id': datarequest.organization_id,
        'open_time': str(datarequest.open_time),
        'accepted_dataset': datarequest.accepted_dataset,
        'close_time': str(datarequest.close_time),
        'closed': datarequest.closed
    }


def _organization_show(context, data_dict):
    return {
    	'id': organization_default_id,
        'display_name': data_dict['id'].title(),
        'name': data_dict['id']
    }


def _generate_basic_ddbb_response(number, organizations=None, closed=None):
    '''
    This methods generates a simulated response from the data base.
    Please note, organizations and states must be list of elements and
    len(organizations) == len(closed) == number. Otherwise,
    an exception will be risen
    '''
    if not organizations:
        organizations = list()
        for _ in range(number):
            organizations.append(None)

    if not closed:
        closed = list()
        for _ in range(number):
            closed.append(False)

    # Check that length of the arrays is correct
    assert number == len(organizations)
    assert number == len(closed)

    response = list()
    for n in range(number):
        response.append(_generate_basic_datarequest(organization_id=organizations[n], 
                                                    closed=closed[n]))

    return response


def _generate_basic_datarequest(id='example_uuidv4', user_id='example_uuidv4_user',
                                title='This is a title', description='This is a basic description',
                                organization_id='example_uuidv4_organization', closed=False):
    datarequest = MagicMock()
    datarequest.id = id
    datarequest.user_id = user_id
    datarequest.title = title
    datarequest.description = description
    datarequest.organization_id = organization_id
    datarequest.open_time = datetime.datetime.now()
    datarequest.closed = closed

    return datarequest


######################################################################
######################### DATA FOR BASIC TESTS #######################
######################################################################

create_request_data = {
    'title': 'title',
    'description': 'description',
    'organization_id': 'organization'
}

show_request_data = {
    'id': 'example_uuidv4'
}

update_request_data = {
    'id': 'example_uuidv4',
    'title': 'title',
    'description': 'description',
    'organization_id': 'organization'
} 


######################################################################
########################### DATAREQUEST_INDEX ########################
######################################################################

org1 = 'org1'
org2 = 'org2'
org3 = 'org3'
organization_default_id = 'organziation_id'
default_offset = 2
default_limit = 3

# First database result
ddbb_response_1 = [_generate_basic_datarequest(organization_id=None)]
expected_result_1 = {
    'count': 1,
    'result': [
        dictice_ddbb_response(ddbb_response_1[0])
    ],
    'facets': {
        'state': {
            'items': [
                {
                    'name': 'open',
                    'display_name': 'Open',
                    'count': 1
                }
            ]
        }
    }
}


# Second database result
ddbb_response_2 = [
    _generate_basic_datarequest(organization_id=org1, closed=True),
    _generate_basic_datarequest(organization_id=org2, closed=False),
    _generate_basic_datarequest(organization_id=org1, closed=True),
    _generate_basic_datarequest(organization_id=org3, closed=False),
    _generate_basic_datarequest(organization_id=org2, closed=True),
    _generate_basic_datarequest(organization_id=org1, closed=False),
    _generate_basic_datarequest(organization_id=None, closed=True),
    _generate_basic_datarequest(organization_id=None, closed=True),
   
]

expected_result_2 = {
    'count': 8,
    'result': [
        dictice_ddbb_response(ddbb_response_2[0]),
        dictice_ddbb_response(ddbb_response_2[1]),
        dictice_ddbb_response(ddbb_response_2[2]),
        dictice_ddbb_response(ddbb_response_2[3]),
        dictice_ddbb_response(ddbb_response_2[4]),
        dictice_ddbb_response(ddbb_response_2[5]),
        dictice_ddbb_response(ddbb_response_2[6]),
        dictice_ddbb_response(ddbb_response_2[7])

    ],
    'facets': {
        'organization': {
            'items': [
                {
                    'name': org1,
                    'display_name': 'Org1',
                    'count': 3
                },
                {
                    'name': org2,
                    'display_name': 'Org2',
                    'count': 2
                },
                {
                    'name': org3,
                    'display_name': 'Org3',
                    'count': 1
                }

            ]
        },
        'state': {
            'items': [
                {
                    'name': 'open',
                    'display_name': 'Open',
                    'count': 3
                },
                {
                    'name': 'closed',
                    'display_name': 'Closed',
                    'count': 5
                }
            ]
        }
    }
}

# The one when the offset and the limit are enabled
expected_result_3 = copy.deepcopy(expected_result_2)
expected_result_3['result'] = expected_result_3['result'][default_offset:default_offset + default_limit]

# TEST CASES
datarequest_index_test_case_1 = {
	'organization_show_func': _organization_show,
	'content': {},
	'expected_ddbb_params': {},
	'ddbb_response': ddbb_response_1,
	'expected_response': expected_result_1
}

datarequest_index_test_case_2 = {
	'organization_show_func': _organization_show,
	'content': {'organization_id': 'fiware'},
	'expected_ddbb_params': {'organization_id': organization_default_id},
	'ddbb_response': ddbb_response_1,
	'expected_response': expected_result_1
}

datarequest_index_test_case_3 = {
	'organization_show_func': _organization_show,
	'content': {'closed': True},
	'expected_ddbb_params': {'closed': True},
	'ddbb_response': ddbb_response_1,
	'expected_response': expected_result_1
}

datarequest_index_test_case_4 = {
	'organization_show_func': _organization_show,
	'content': {'organization_id': 'fiware', 'closed': True},
	'expected_ddbb_params': {'organization_id': organization_default_id, 'closed': True},
	'ddbb_response': ddbb_response_1,
	'expected_response': expected_result_1
}

datarequest_index_test_case_5 = {
	'organization_show_func': _organization_show,
	'content': {},
	'expected_ddbb_params': {},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_2
}

datarequest_index_test_case_6 = {
	'organization_show_func': _organization_show,
	'content': {'organization_id': 'fiware'},
	'expected_ddbb_params': {'organization_id': organization_default_id},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_2
}

datarequest_index_test_case_7 = {
	'organization_show_func': _organization_show,
	'content': {'closed': True},
	'expected_ddbb_params': {'closed': True},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_2
}

datarequest_index_test_case_8 = {
	'organization_show_func': _organization_show,
	'content': {'organization_id': 'fiware', 'closed': True},
	'expected_ddbb_params': {'organization_id': organization_default_id, 'closed': True},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_2
}

datarequest_index_test_case_9 = {
	'organization_show_func': _organization_show,
	'content': {'offset': default_offset, 'limit': default_limit},
	'expected_ddbb_params': {},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_3
}

datarequest_index_test_case_10 = {
	'organization_show_func': _organization_show,
	'content': {'organization_id': 'fiware', 'offset': default_offset, 'limit': default_limit},
	'expected_ddbb_params': {'organization_id': organization_default_id},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_3
}

datarequest_index_test_case_11 = {
	'organization_show_func': _organization_show,
	'content': {'closed': True, 'offset': default_offset, 'limit': default_limit},
	'expected_ddbb_params': {'closed': True},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_3
}

datarequest_index_test_case_12 = {
	'organization_show_func': _organization_show,
	'content': {'organization_id': 'fiware', 'closed': True, 'offset': default_offset, 'limit': default_limit},
	'expected_ddbb_params': {'organization_id': organization_default_id, 'closed': True},
	'ddbb_response': ddbb_response_2,
	'expected_response': expected_result_3
}
