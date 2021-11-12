# encoding: utf-8

import unittest

from ckanext.datarequests.plugin.pylons_plugin import MixinPlugin

from mock import MagicMock, patch
from parameterized import parameterized

TOTAL_ACTIONS = 13
COMMENTS_ACTIONS = 5
ACTIONS_NO_COMMENTS = TOTAL_ACTIONS - COMMENTS_ACTIONS


class DataRequestPylonsPluginTest(unittest.TestCase):

    @parameterized.expand([
        (True,),
        (False,)
    ])
    def test_before_map(self, comments_enabled):

        urls_set = 15
        mapa_calls = urls_set if comments_enabled else urls_set - 3

        # Configure config and get instance
        self.plg_instance = MixinPlugin()
        self.plg_instance.comments_enabled = comments_enabled

        mock_icon = 'icon'
        get_question_icon_patch = patch('ckanext.datarequests.common.get_question_icon', return_value=mock_icon)
        get_question_icon_patch.start()
        self.addCleanup(get_question_icon_patch.stop)

        # Test
        mapa = MagicMock()
        dr_basic_path = 'datarequest'
        self.plg_instance.before_map(mapa)

        self.assertEquals(mapa_calls, mapa.connect.call_count)
        mapa.connect.assert_any_call(
            'datarequests_index', "/%s" % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='index', conditions={'method': ['GET']})

        mapa.connect.assert_any_call(
            'datarequest.index', "/%s" % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='index', conditions={'method': ['GET']})

        mapa.connect.assert_any_call(
            'datarequest.new', '/%s/new' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='new', conditions={'method': ['GET', 'POST']})

        mapa.connect.assert_any_call(
            'show_datarequest', '/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='show', conditions={'method': ['GET']}, ckan_icon=mock_icon)

        mapa.connect.assert_any_call(
            'datarequest.show', '/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='show', conditions={'method': ['GET']}, ckan_icon=mock_icon)

        mapa.connect.assert_any_call(
            'datarequest.update', '/%s/edit/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='update', conditions={'method': ['GET', 'POST']})

        mapa.connect.assert_any_call(
            'datarequest.delete', '/%s/delete/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='delete', conditions={'method': ['POST']})

        mapa.connect.assert_any_call(
            'datarequest.close', '/%s/close/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='close', conditions={'method': ['GET', 'POST']})

        mapa.connect.assert_any_call(
            'organization_datarequests',
            '/organization/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='organization_datarequests', conditions={'method': ['GET']},
            ckan_icon=mock_icon)

        mapa.connect.assert_any_call(
            'user_datarequests',
            '/user/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='user_datarequests', conditions={'method': ['GET']},
            ckan_icon=mock_icon)

        mapa.connect.assert_any_call(
            'user_datarequests',
            '/user/%s/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='user_datarequests', conditions={'method': ['GET']},
            ckan_icon=mock_icon)

        mapa.connect.assert_any_call(
            'datarequest.follow', '/%s/follow/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='follow', conditions={'method': ['POST']})

        mapa.connect.assert_any_call(
            'datarequest.unfollow', '/%s/unfollow/{id}' % dr_basic_path,
            controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
            action='unfollow', conditions={'method': ['POST']})

        if comments_enabled:
            mapa.connect.assert_any_call(
                'comment_datarequest', '/%s/comment/{id}' % dr_basic_path,
                controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                action='comment', conditions={'method': ['GET', 'POST']}, ckan_icon='comment')

            mapa.connect.assert_any_call(
                'datarequest.comment', '/%s/comment/{id}' % dr_basic_path,
                controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                action='comment', conditions={'method': ['GET', 'POST']}, ckan_icon='comment')

            mapa.connect.assert_any_call(
                'datarequest.delete_comment', '/%s/comment/{datarequest_id}/delete/{comment_id}' % dr_basic_path,
                controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                action='delete_comment', conditions={'method': ['GET', 'POST']})
