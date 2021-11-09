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
                f"/{constants.DATAREQUESTS_MAIN_PATH}",
                "index",
                ui_controller.index,
            ),
            (
                f"/{constants.DATAREQUESTS_MAIN_PATH}/new",
                "new",
                ui_controller.new,
            ),
            (
                f"/{constants.DATAREQUESTS_MAIN_PATH}/<id>",
                "show",
                ui_controller.show,
            ),
            (
                f"/{constants.DATAREQUESTS_MAIN_PATH}/edit/<id>",
                "update",
                ui_controller.update,
            ),
            (
                f"/{constants.DATAREQUESTS_MAIN_PATH}/delete/<id>",
                "delete",
                ui_controller.delete,
            ),
            (
                f"/{constants.DATAREQUESTS_MAIN_PATH}/close/<id>",
                "close",
                ui_controller.close,
            ),
            (
                f"/{constants.DATAREQUESTS_MAIN_PATH}/follow/<datarequest_id>",
                "follow",
                ui_controller.follow,
            ),
            (
                f"/{constants.DATAREQUESTS_MAIN_PATH}/unfollow/<datarequest_id>",
                "unfollow",
                ui_controller.unfollow,
            ),
            (
                f"/organization/{constants.DATAREQUESTS_MAIN_PATH}/<id>",
                "organization",
                ui_controller.organization,
            ),
            (
                f"/user/{constants.DATAREQUESTS_MAIN_PATH}/<id>",
                "user",
                ui_controller.user,
            ),
        ]

        if self.comments_enabled:
            rules.extend(
                [
                    (
                        f"/{constants.DATAREQUESTS_MAIN_PATH}/comment/<id>",
                        "comment",
                        ui_controller.comment,
                    ),
                    (
                        f"/{constants.DATAREQUESTS_MAIN_PATH}/comment/<datarequest_id>/delete/<comment_id>",
                        "delete_comment",
                        ui_controller.delete_comment,
                    ),
                ]
            )

        for rule in rules:
            datarequests_bp.add_url_rule(rule[0], endpoint=rule[1], view_func=rule[2])

        return [datarequests_bp]
