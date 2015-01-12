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

import ckanext.datarequests.validator as validator
import unittest
import random

from mock import MagicMock
from nose_parameterized import parameterized


def generate_string(length):
    return ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                   for i in range(length))


class ValidatorTest(unittest.TestCase):

    def setUp(self):
        self.context = MagicMock()
        self.request_data = {
            'title': 'Example Title',
            'description': 'Example description',
            'organization': 'uuid-example'
        }

        # Mocks
        self._tk = validator.tk
        validator.tk = MagicMock()
        validator.tk.ValidationError = self._tk.ValidationError
        validator.tk._ = self._tk._

        self._db = validator.db
        validator.db = MagicMock()
        validator.db.DataRequest.datarequest_exists.return_value = False

    def tearDown(self):
        validator.tk = self._tk

    def test_validate_valid_data_request(self):
        context = MagicMock()
        self.assertIsNone(validator.validate_datarequest(context, self.request_data))

    @parameterized.expand([
        ('Title', generate_string(validator.constants.NAME_MAX_LENGTH + 1), False,
            'Title must be a maximum of %d characters long' % validator.constants.NAME_MAX_LENGTH),
        ('Title', '', False, 'Title cannot be empty'),
        ('Title', 'DR Example Tile', True, 'That title is already in use'),
        ('Description', generate_string(validator.constants.DESCRIPTION_MAX_LENGTH + 1), False,
            'Description must be a maximum of %d characters long' % validator.constants.DESCRIPTION_MAX_LENGTH),

    ])
    def test_validate_name_description(self, field, value, title_exists, excepction_msg):
        context = MagicMock()
        # request_data fields are always in lowercase
        self.request_data[field.lower()] = value
        validator.db.DataRequest.datarequest_exists.return_value = title_exists

        with self.assertRaises(self._tk.ValidationError) as context:
            validator.validate_datarequest(context, self.request_data)

        self.assertEquals({field: [excepction_msg]},
                          context.exception.error_dict)

    def test_invalid_org(self):
        org_validator = validator.tk.get_validator.return_value
        org_validator.side_effect = self._tk.ValidationError({'Organization': 'Invalid ORG'})

        with self.assertRaises(self._tk.ValidationError) as context:
            validator.validate_datarequest(context, self.request_data)

        self.assertEquals({'Organization': ['Organization is not valid']},
                          context.exception.error_dict)
