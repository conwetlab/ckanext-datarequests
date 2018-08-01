/*
 * (C) Copyright 2015 CoNWeT Lab., Universidad Politécnica de Madrid
 *
 * This file is part of CKAN Data Requests Extension.
 *
 * CKAN Data Requests Extension is free software: you can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * CKAN Data Requests Extension is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with CKAN Data Requests Extension. If not, see
 * <http://www.gnu.org/licenses/>.
 *
 */

(function() {
    
    var UPDATE_COMMENT_BASIC_ID = 'update-comment-';
    var DISCARD_COMMENT_BASIC_ID = 'comment-discard-'

    $("[id^=" + UPDATE_COMMENT_BASIC_ID + "]").on('click', function(e) {
        comment_id = $(this).attr('id').replace(UPDATE_COMMENT_BASIC_ID, '');

        if ($('#comment-' + comment_id).hasClass('hide')) {
            $('#' + DISCARD_COMMENT_BASIC_ID + comment_id).click();
        } else {
            $('#comment-' + comment_id).addClass('hide');
            $('#comment-form-' + comment_id).removeClass('hide');
        }
    });

    $("[id^=" + DISCARD_COMMENT_BASIC_ID + "]").on('click', function(e) {
        comment_id = $(this).attr('id').replace(DISCARD_COMMENT_BASIC_ID, '');

        $('#comment-' + comment_id).removeClass('hide');
        $('#comment-form-' + comment_id).addClass('hide');

        e.preventDefault();
    });

    $(document).ready(function() {
        var anchorName = 'comment_focus';

        if ($('[name="' + anchorName + '"]').length) {
            window.location.hash = anchorName;
        }
    });

})();