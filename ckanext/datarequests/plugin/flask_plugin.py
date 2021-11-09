# encoding: utf-8

import ckan.plugins as p
from flask import Blueprint

from ckanext.datarequests import constants
from . import ui_controller


datarequests_bp = Blueprint("datarequest", __name__)


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        rules = [
            (
                "/" + constants.DATAREQUESTS_MAIN_PATH,
                "index",
                ui_controller.index,
            ),
            (
                "/{}/new".format(constants.DATAREQUESTS_MAIN_PATH),
                "new",
                ui_controller.new,
            ),
            (
                "/{}/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "show",
                ui_controller.show,
            ),
            (
                "/{}/edit/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "update",
                ui_controller.update,
            ),
            (
                "/{}/delete/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "delete",
                ui_controller.delete,
            ),
            (
                "/{}/close/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "close",
                ui_controller.close,
            ),
            (
                "/{}/follow/<datarequest_id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "follow",
                ui_controller.follow,
            ),
            (
                "/{}/unfollow/<datarequest_id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "unfollow",
                ui_controller.unfollow,
            ),
            (
                "/organization/{}/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "organization",
                ui_controller.organization,
            ),
            (
                "/user/{}/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                "user",
                ui_controller.user,
            ),
        ]

        if self.comments_enabled:
            rules.extend(
                [
                    (
                        "/{}/comment/<id>".format(constants.DATAREQUESTS_MAIN_PATH),
                        "comment",
                        ui_controller.comment,
                    ),
                    (
                        "/{}/comment/<datarequest_id>/delete/<comment_id>".format(
                            constants.DATAREQUESTS_MAIN_PATH),
                        "delete_comment",
                        ui_controller.delete_comment,
                    ),
                ]
            )

        for rule in rules:
            datarequests_bp.add_url_rule(rule[0], endpoint=rule[1], view_func=rule[2])

        return [datarequests_bp]
