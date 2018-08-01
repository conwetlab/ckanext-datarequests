# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016 CoNWeT Lab., Universidad Politécnica de Madrid

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

import unittest
import ckanext.datarequests.db as db

from mock import MagicMock
from nose_parameterized import parameterized


class DBTest(unittest.TestCase):

    EXAMPLE_UUID = 'example_uuid_v4'
    FREE_TEXT_QUERY = 'free-text'

    def setUp(self):
        # Restart databse initial status
        db.DataRequest = None
        db.Comment = None
        db.DataRequestFollower = None

        # Create mocks
        self._sa = db.sa
        db.sa = MagicMock()

        self._func = db.func
        db.func = MagicMock()

        self._or_ = db.or_
        db.or_ = MagicMock()

    def tearDown(self):
        db.Comment = None
        db.DataRequest = None
        db.DataRequestFollower = None
        db.sa = self._sa
        db.func = self._func
        db.or_ = self._or_

    def _test_get(self, table):
        '''
        Aux method for Comment and Data Requests
        '''
        db_response = [MagicMock(), MagicMock(), MagicMock()]

        query_result = MagicMock()
        query_result.all.return_value = db_response

        final_query = MagicMock()
        final_query.filter_by.return_value = query_result

        query = MagicMock()
        query.autoflush = MagicMock(return_value=final_query)

        model = MagicMock()
        model.DomainObject = object
        model.Session.query = MagicMock(return_value=query)

        # Init the database
        db.init_db(model)

        # Call the method
        params = {
            'title': 'Default Title',
            'organization_id': 'example_uuid_v4'
        }
        result = getattr(db, table).get(**params)

        # Assertions
        self.assertEquals(db_response, result)
        final_query.filter_by.assert_called_once_with(**params)

    def _test_get_ordered_by_date(self, table, time_column, params):

        db_response = [MagicMock(), MagicMock(), MagicMock()]

        query_result = MagicMock()
        query_result.all.return_value = db_response

        no_ordered = MagicMock()
        no_ordered.order_by.return_value = query_result

        final_query = MagicMock()
        final_query.filter.return_value = final_query
        final_query.filter_by.return_value = no_ordered

        query = MagicMock()
        query.autoflush = MagicMock(return_value=final_query)

        model = MagicMock()
        model.DomainObject = object
        model.Session.query = MagicMock(return_value=query)

        # Init the database
        db.init_db(model)
        # Mapping
        table = getattr(db, table)
        time_column_value = MagicMock()
        title_column_value = MagicMock()
        description_column_value = MagicMock()
        setattr(table, time_column, time_column_value)
        setattr(table, 'title', title_column_value)
        setattr(table, 'description', description_column_value)

        # Call the method
        result = table.get_ordered_by_date(**params)

        # Calculate expected filter parameters
        expected_filter_by_params = params.copy()

        if 'q' in expected_filter_by_params:
            expected_filter_by_params.pop('q')

        if 'desc' in expected_filter_by_params:
            expected_filter_by_params.pop('desc')

        query = '%{0}%'.format(params['q']) if 'q' in params else None
        desc = True if 'desc' in params and params['desc'] is True else False

        # Assertions
        self.assertEquals(db_response, result)
        order = time_column_value.desc() if desc else time_column_value.asc()
        no_ordered.order_by.assert_called_once_with(order)
        final_query.filter_by.assert_called_once_with(**expected_filter_by_params)

        # This only happens with the table of data requests
        if query:
            title_column_value.ilike.assert_called_once_with(query)
            description_column_value.ilike.assert_called_once_with(query)
            db.or_.assert_called_once_with(title_column_value.ilike.return_value,
                                           description_column_value.ilike.return_value)

            final_query.filter.assert_called_once_with(db.or_.return_value)

    def test_initdb_not_initialized(self):

        table_data_request = MagicMock()
        table_comment = MagicMock()
        table_datarequest_follower = MagicMock()

        db.sa.Table = MagicMock(side_effect=[table_data_request, table_comment, table_datarequest_follower])

        # Call the function
        model = MagicMock()
        db.init_db(model)

        # Assert that table method has been called
        self.assertEquals(3, db.sa.Table.call_count)
        model.meta.mapper.assert_any_call(db.DataRequest, table_data_request)
        model.meta.mapper.assert_any_call(db.Comment, table_comment)
        model.meta.mapper.assert_any_call(db.DataRequestFollower, table_datarequest_follower)

    def test_initdb_initialized(self):
        db.DataRequest = MagicMock()
        db.Comment = MagicMock()
        db.DataRequestFollower = MagicMock()

        # Call the function
        model = MagicMock()
        db.init_db(model)

        # Assert that table method has been called
        self.assertEquals(0, db.sa.Table.call_count)
        self.assertEquals(0, model.meta.mapper.call_count)

    def test_datarequest_get(self):
        self._test_get('DataRequest')

    @parameterized.expand([
        (None, False),
        (1,    True)
    ])
    def test_datarequest_exist(self, first_result, expected_result):

        title = 'DataRequest Title'

        # Prepare the mocks
        def _lower(text):
            # If expected_result == true it's because lower is supossed
            # to return the same result in the two calls
            if expected_result:
                return title.lower()
            else:
                return text

        db.func.lower.side_effect = _lower

        # Query
        query_result = MagicMock()
        query_result.first.return_value = first_result

        final_query = MagicMock()
        final_query.filter.return_value = query_result

        query = MagicMock()
        query.autoflush = MagicMock(return_value=final_query)

        model = MagicMock()
        model.DomainObject = object
        model.Session.query = MagicMock(return_value=query)

        # Init the database
        db.init_db(model)

        # Call the method
        db.DataRequest.title = 'TITLE'
        result = db.DataRequest.datarequest_exists(title)

        # Assertion
        self.assertEquals(expected_result, result)
        db.func.lower.assert_any_call(db.DataRequest.title)
        db.func.lower.assert_any_call(title)
        # If expected_result == true is because lower is supossed
        # to return the same result in the two calls and the
        # equalization of these results must be True
        final_query.filter.assert_called_once_with(expected_result)

    @parameterized.expand([
        ({'organization_id': EXAMPLE_UUID},),
        ({'user_id': EXAMPLE_UUID},),
        ({'closed': True},),
        ({'closed': False},),
        ({'desc': True},),
        ({'desc': False},),
        ({'q': 'free-text'},)
    ])
    def test_datarequest_get_ordered_by_date(self, params):
        self._test_get_ordered_by_date('DataRequest', 'open_time', params)

    def test_get_open_datarequests_number(self):

        n_datarequests = 7
        count = 'example'

        db.func = MagicMock()
        db.func.count.return_value = count

        filter_by = MagicMock()
        filter_by.scalar.return_value = n_datarequests

        query = MagicMock()
        query.filter_by = MagicMock(return_value=filter_by)

        model = MagicMock()
        model.DomainObject = object
        model.Session.query = MagicMock(return_value=query)

        # Init the database
        db.init_db(model)

        # Call the method
        db.DataRequest.id = 'id'
        result = db.DataRequest.get_open_datarequests_number()

        # Assertions
        self.assertEquals(n_datarequests, result)
        query.filter_by.assert_called_once_with(closed=False)
        model.Session.query.assert_called_once_with(count)
        db.func.count.assert_called_once_with(db.DataRequest.id)

    def test_comment_get(self):
        self._test_get('Comment')

    @parameterized.expand([
        ({'datarequest_id': 'example_uuid_v4'},),
        ({'datarequest_id': 'example_uuid_v4', 'desc': False},),
        ({'datarequest_id': 'example_uuid_v4', 'desc': True},),
    ])
    def test_comment_get_ordered_by_date(self, params):
        self._test_get_ordered_by_date('Comment', 'time', params)

    def test_get_datarequests_comments(self):

        n_comments = 7
        count = 'example'

        db.func = MagicMock()
        db.func.count.return_value = count

        filter_by = MagicMock()
        filter_by.scalar.return_value = n_comments

        query = MagicMock()
        query.filter_by = MagicMock(return_value=filter_by)

        model = MagicMock()
        model.DomainObject = object
        model.Session.query = MagicMock(return_value=query)

        # Init the database
        db.init_db(model)

        # Call the method
        params = {
            'datarequest_id': 'example_uuid_v4'
        }
        db.Comment.id = 'id'
        result = db.Comment.get_comment_datarequests_number(**params)

        # Assertions
        self.assertEquals(n_comments, result)
        query.filter_by.assert_called_once_with(**params)
        model.Session.query.assert_called_once_with(count)
        db.func.count.assert_called_once_with(db.Comment.id)

    def test_datarequest_follower_get(self):
        self._test_get('DataRequestFollower')

    def test_get_datarequest_followers_number(self):

        n_followers = 7
        count = 'example'

        db.func = MagicMock()
        db.func.count.return_value = count

        filter_by = MagicMock()
        filter_by.scalar.return_value = n_followers

        query = MagicMock()
        query.filter_by = MagicMock(return_value=filter_by)

        model = MagicMock()
        model.DomainObject = object
        model.Session.query = MagicMock(return_value=query)

        # Init the database
        db.init_db(model)

        # Call the method
        params = {
            'datarequest_id': 'example_uuid_v4'
        }
        db.DataRequestFollower.id = 'id'
        result = db.DataRequestFollower.get_datarequest_followers_number(**params)

        # Assertions
        self.assertEquals(n_followers, result)
        query.filter_by.assert_called_once_with(**params)
        model.Session.query.assert_called_once_with(count)
        db.func.count.assert_called_once_with(db.DataRequestFollower.id)

