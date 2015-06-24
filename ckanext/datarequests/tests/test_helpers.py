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

import ckanext.datarequests.helpers as helpers
import unittest

from mock import MagicMock


class HelpersTest(unittest.TestCase):

    def setUp(self):
        self._tk = helpers.tk
        helpers.tk = MagicMock()

        self._model = helpers.model
        helpers.model = MagicMock()

        self._db = helpers.db
        helpers.db = MagicMock()

    def tearDown(self):
        helpers.tk = self._tk
        helpers.model = self._model
        helpers.db = self._db

    def test_get_comments_number(self):
        # Mocking
        n_comments = 3
        helpers.db.Comment.get_datarequest_comments.return_value = 3

        # Call the function
        datarequest_id = 'example_uuidv4'
        result = helpers.get_comments_number(datarequest_id)

        # Assertions
        helpers.db.init_db.assert_called_once_with(helpers.model)
        helpers.db.Comment.get_datarequest_comments.assert_called_once_with(datarequest_id=datarequest_id)
        self.assertEquals(result, n_comments)

    def test_get_comments_badge(self):
        # Mocking
        n_comments = 3
        helpers.db.Comment.get_datarequest_comments.return_value = 3

        # Call the function
        datarequest_id = 'example_uuidv4'
        result = helpers.get_comments_badge(datarequest_id)

        # Assertions
        helpers.db.init_db.assert_called_once_with(helpers.model)
        helpers.db.Comment.get_datarequest_comments.assert_called_once_with(datarequest_id=datarequest_id)
        self.assertEquals(result, helpers.tk.render_snippet.return_value)
        helpers.tk.render_snippet.assert_called_once_with('datarequests/snippets/comments_badge.html',
                                                          {'comments_count': n_comments})
