# encoding: utf-8

import ckan.plugins as p

from ckanext.datarequests import common, constants


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    ######################################################################
    ############################## IROUTES ###############################
    ######################################################################

    def before_map(self, mapper):
        from routes.mapper import SubMapper
        controller_map = SubMapper(
            mapper, controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI')

        m = SubMapper(controller_map, path_prefix="/" + constants.DATAREQUESTS_MAIN_PATH)

        # Data Requests index
        m.connect('datarequests_index', '', action='index', conditions={'method': ['GET']})
        m.connect('datarequest.index', '', action='index', conditions={'method': ['GET']})

        # Create a Data Request
        m.connect('datarequest.new', '/new', action='new', conditions={'method': ['GET', 'POST']})

        # Show a Data Request
        m.connect('show_datarequest', '/{id}',
                  action='show', conditions={'method': ['GET']}, ckan_icon=common.get_question_icon())
        m.connect('datarequest.show', '/{id}',
                  action='show', conditions={'method': ['GET']}, ckan_icon=common.get_question_icon())

        # Update a Data Request
        m.connect('datarequest.update', '/edit/{id}',
                  action='update', conditions={'method': ['GET', 'POST']})

        # Delete a Data Request
        m.connect('datarequest.delete', '/delete/{id}',
                  action='delete', conditions={'method': ['POST']})

        # Close a Data Request
        m.connect('datarequest.close', '/close/{id}',
                  action='close', conditions={'method': ['GET', 'POST']})

        # Follow & Unfollow
        m.connect('datarequest.follow', '/follow/{id}',
                  action='follow', conditions={'method': ['POST']})

        m.connect('datarequest.unfollow', '/unfollow/{id}',
                  action='unfollow', conditions={'method': ['POST']})

        if self.comments_enabled:
            # Comment, update and view comments (of) a Data Request
            m.connect('comment_datarequest', '/comment/{id}',
                      action='comment', conditions={'method': ['GET', 'POST']}, ckan_icon='comment')
            m.connect('datarequest.comment', '/comment/{id}',
                      action='comment', conditions={'method': ['GET', 'POST']}, ckan_icon='comment')

            # Delete data request
            m.connect('datarequest.delete_comment', '/comment/{datarequest_id}/delete/{comment_id}',
                      action='delete_comment', conditions={'method': ['GET', 'POST']})

        list_datarequests_map = SubMapper(
            controller_map, conditions={'method': ['GET']}, ckan_icon=common.get_question_icon())

        # Data Requests that belong to an organization
        list_datarequests_map.connect(
            'organization_datarequests', '/organization/%s/{id}' % constants.DATAREQUESTS_MAIN_PATH,
            action='organization_datarequests')
        list_datarequests_map.connect(
            'datarequest.organization', '/organization/%s/{id}' % constants.DATAREQUESTS_MAIN_PATH,
            action='organization_datarequests')

        # Data Requests that belong to a user
        list_datarequests_map.connect(
            'user_datarequests', '/user/%s/{id}' % constants.DATAREQUESTS_MAIN_PATH,
            action='user_datarequests')
        list_datarequests_map.connect(
            'datarequest.user', '/user/%s/{id}' % constants.DATAREQUESTS_MAIN_PATH,
            action='user_datarequests')

        return mapper
