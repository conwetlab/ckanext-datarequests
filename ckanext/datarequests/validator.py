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

import constants
import ckan.plugins.toolkit as tk
import ckanext.datarequests.db as db
import plugin as datarequests
import datetime


def validate_datarequest(context, request_data):

    errors = {}

    # Check name
    if len(request_data['title']) > constants.NAME_MAX_LENGTH:
        errors[tk._('Title')] = [tk._('Title must be a maximum of %d characters long') % constants.NAME_MAX_LENGTH]

    if not request_data['title']:
        errors[tk._('Title')] = [tk._('Title cannot be empty')]

    # Title is only checked in the database when it's correct
    avoid_existing_title_check = context['avoid_existing_title_check'] if 'avoid_existing_title_check' in context else False

    if 'Title' not in errors and not avoid_existing_title_check:
        if db.DataRequest.datarequest_exists(request_data['title']):
            errors[tk._('Title')] = [tk._('That title is already in use')]

    # Check description
    if datarequests.get_config_bool_value('ckan.datarequests.description_required', False) and not request_data['description']:
        errors[tk._('Description')] = [tk._('Description cannot be empty')]

    if len(request_data['description']) > constants.DESCRIPTION_MAX_LENGTH:
        errors[tk._('Description')] = [tk._('Description must be a maximum of %d characters long') % constants.DESCRIPTION_MAX_LENGTH]

    # Check organization
    if request_data['organization_id']:
        try:
            tk.get_validator('group_id_exists')(request_data['organization_id'], context)
        except Exception:
            errors[tk._('Organization')] = [tk._('Organization is not valid')]

    if len(errors) > 0:
        raise tk.ValidationError(errors)


def validate_datarequest_closing(context, request_data):
    if tk.h.closing_circumstances_enabled:
        close_circumstance = request_data.get('close_circumstance', None)
        if not close_circumstance:
            raise tk.ValidationError({tk._('Circumstances'): [tk._('Circumstances cannot be empty')]})
        condition = request_data.get('condition', None)
        if condition:
            if condition == 'nominate_dataset' and request_data.get('accepted_dataset_id', '') == '':
                raise tk.ValidationError({tk._('Accepted dataset'): [tk._('Accepted dataset cannot be empty')]})
            elif condition == 'nominate_approximate_date':
                if request_data.get('approx_publishing_date', '') == '':
                    raise tk.ValidationError({tk._('Approximate publishing date'): [tk._('Approximate publishing date cannot be empty')]})
                try:
                    # This validation is required for the Safari browser as the date type input is not supported and falls back to using a text type input
                    # SQLAlchemy throws an error if the date value is not in the format yyyy-mm-dd
                    datetime.datetime.strptime(request_data.get('approx_publishing_date', ''), '%Y-%m-%d')
                except ValueError:
                    raise tk.ValidationError({tk._('Approximate publishing date'): [tk._('Approximate publishing date must be in format yyyy-mm-dd')]})

    accepted_dataset_id = request_data.get('accepted_dataset_id', '')
    if accepted_dataset_id:
        try:
            tk.get_validator('package_name_exists')(accepted_dataset_id, context)
        except Exception:
            raise tk.ValidationError({tk._('Accepted dataset'): [tk._('Dataset not found')]})


def validate_comment(context, request_data):
    comment = request_data.get('comment', '')

    # Check if the data request exists
    try:
        datarequest = tk.get_action(constants.SHOW_DATAREQUEST)(context, {'id': request_data['datarequest_id']})
    except Exception:
        raise tk.ValidationError({tk._('Data Request'): [tk._('Data Request not found')]})

    if not comment or len(comment) <= 0:
        raise tk.ValidationError({tk._('Comment'): [tk._('Comments must be a minimum of 1 character long')]})

    if len(comment) > constants.COMMENT_MAX_LENGTH:
        raise tk.ValidationError({tk._('Comment'): [tk._('Comments must be a maximum of %d characters long') % constants.COMMENT_MAX_LENGTH]})

    return datarequest
