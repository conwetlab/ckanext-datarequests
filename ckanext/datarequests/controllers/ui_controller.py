# -*- coding: utf-8 -*-

from ckan.plugins.toolkit import BaseController

from . import controller_functions as controller


class DataRequestsUI(BaseController):

    def index(self):
        return controller.index()

    def new(self):
        return controller.new()

    def show(self, id):
        return controller.show(id)

    def update(self, id):
        return controller.update(id)

    def delete(self, id):
        return controller.delete(id)

    def organization_datarequests(self, id):
        return controller.organization(id)

    def user_datarequests(self, id):
        return controller.user(id)

    def close(self, id):
        return controller.close(id)

    def comment(self, id):
        return controller.comment(id)

    def delete_comment(self, datarequest_id, comment_id):
        return controller.delete_comment(datarequest_id, comment_id)

    def follow(self, datarequest_id):
        return controller.follow(datarequest_id)

    def unfollow(self, datarequest_id):
        return controller.unfollow(datarequest_id)
