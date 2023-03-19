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

from ckan import model
from ckan.common import c
import ckan.plugins.toolkit as tk

from . import db


def get_comments_number(datarequest_id):
    # DB should be intialized
    db.init_db(model)
    return db.Comment.get_comment_datarequests_number(datarequest_id=datarequest_id)


def get_comments_badge(datarequest_id):
    return tk.render_snippet('datarequests/snippets/badge.html',
                             {'comments_count': get_comments_number(datarequest_id)})


def get_open_datarequests_number():
    # DB should be initialized
    db.init_db(model)
    return db.DataRequest.get_open_datarequests_number()


def is_following_datarequest(datarequest_id):
    # DB should be intialized
    db.init_db(model)
    return len(db.DataRequestFollower.get(datarequest_id=datarequest_id, user_id=c.userobj.id)) > 0


def get_open_datarequests_badge(show_badge):
    '''The snippet is only returned when show_badge == True'''
    if show_badge:
        return tk.render_snippet('datarequests/snippets/badge.html',
                                 {'comments_count': get_open_datarequests_number()})
    else:
        return ''


def get_closing_circumstances():
    """Returns a list of datarequest closing circumstances from admin config

    :rtype: List of circumstance objects {'circumstance': circumstance, 'condition': condition}

    """
    closing_circumstances = []
    for closing_circumstance in tk.config.get('ckan.datarequests.closing_circumstances', '').split('\n'):
        option = closing_circumstance.split('|')
        circumstance = option[0].strip()
        condition = option[1].strip() if len(option) == 2 else ''
        closing_circumstances.append({'circumstance': circumstance, 'condition': condition})

    return closing_circumstances
