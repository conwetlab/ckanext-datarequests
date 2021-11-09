# -*- coding: utf-8 -*-

from ckan.plugins.toolkit import BaseController

from . import controller_functions


class DataRequestsUI(BaseController):

    def index(self):
        return ui_controller.index()

    def new(self):
        return ui_controller.new()

    def show(self, id):
        return ui_controller.show(id)

    def update(self, id):
        return ui_controller.update(id)

    def delete(self, id):
        return ui_controller.delete(id)

    def organization_datarequests(self, id):
        return ui_controller.organization(id)

    def user_datarequests(self, id):
        return ui_controller.user(id)

    def close(self, id):
        return ui_controller.close(id)

    def comment(self, id):
        return ui_controller.comment(id)

    def delete_comment(self, datarequest_id, comment_id):
        return ui_controller.delete_comment(datarequest_id, comment_id)

    def follow(self, datarequest_id):
        return ui_controller.follow(datarequest_id)

    def unfollow(self, datarequest_id):
        return ui_controller.unfollow(datarequest_id)
