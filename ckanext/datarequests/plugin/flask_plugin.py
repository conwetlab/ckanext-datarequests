# encoding: utf-8

import ckan.plugins as p
from flask import Blueprint

from ckanext.datarequests import constants
from ckanext.datarequests.controllers import controller_functions


datarequests_bp = Blueprint("datarequest", __name__)


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        rules = [
            (
                "/" + constants.DATAREQUESTS_MAIN_PATH,
                "index",
                controller_functions.index,
            ),
            (
                "/{}/new".format(constants.DATAREQUESTS_MAIN_PATH),
                "new",
                controller_functions.new,
            ),
            (
                "/{}/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "show",
                controller_functions.show,
            ),
            (
                "/{}/edit/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "update",
                controller_functions.update,
            ),
            (
                "/{}/delete/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "delete",
                controller_functions.delete,
            ),
            (
                "/{}/close/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "close",
                controller_functions.close,
            ),
            (
                "/{}/follow/<datarequest_id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "follow",
                controller_functions.follow,
            ),
            (
                "/{}/unfollow/<datarequest_id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "unfollow",
                controller_functions.unfollow,
            ),
            (
                "/organization/{}/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "organization",
                controller_functions.organization,
            ),
            (
                "/user/{}/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "user",
                controller_functions.user,
            ),
        ]

        if self.comments_enabled:
            rules.extend(
                [
                    (
                        "/{}/comment/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                        "comment",
                        controller_functions.comment,
                    ),
                    (
                        "/{}/comment/<datarequest_id>/delete/<comment_id>".format(
                            constants.DATAREQUESTS_MAIN_PATH),
                        "delete_comment",
                        controller_functions.delete_comment,
                    ),
                ]
            )

        for rule in rules:
            datarequests_bp.add_url_rule(rule[0], endpoint=rule[1], view_func=rule[2])

        return [datarequests_bp]
