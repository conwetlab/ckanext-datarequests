# -*- coding: utf-8 -*-

# Copyright (c) 2016 CoNWeT Lab., Universidad Politécnica de Madrid

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
# along with CKAN Data Requests Extension.  If not, see <http://www.gnu.org/licenses/>.

from nose_parameterized import parameterized
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from subprocess import Popen

import ckan.lib.search.index as search_index
import ckan.model as model
import ckanext.datarequests.db as db
import os
import random
import string
import unittest


def _generate_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in xrange(length))


class TestSelenium(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env = os.environ.copy()
        env['DEBUG'] = 'True'
        env['OAUTHLIB_INSECURE_TRANSPORT'] = 'True'
        cls._process = Popen(['paster', 'serve', 'test.ini'], env=env)

    @classmethod
    def tearDownClass(cls):
        cls._process.terminate()

    def clearBBDD(self):
        # Clean Solr
        search_index.clear_index()

        # Clean the database
        model.repo.rebuild_db()

        # Delete previous users
        db.init_db(model)
        datarequests = db.DataRequest.get()
        for datarequest in datarequests:
            model.Session.delete(datarequest)

        comments = db.Comment.get()
        for comment in comments:
            model.Session.delete(comment)

        model.Session.commit()

    def setUp(self):
        self.clearBBDD()

        if 'WEB_DRIVER_URL' in os.environ and 'CKAN_SERVER_URL' in os.environ:
            self.driver = webdriver.Remote(os.environ['WEB_DRIVER_URL'], webdriver.DesiredCapabilities.FIREFOX.copy())
            self.base_url = os.environ['CKAN_SERVER_URL']
        else:
            self.driver = webdriver.Firefox()
            self.base_url = 'http://127.0.0.1:5000/'

        self.driver.implicitly_wait(5)
        self.driver.set_window_size(1024, 768)

    def tearDown(self):
        self.clearBBDD()
        self.driver.quit()

    def assert_fields_disabled(self, fields):
        for field in fields:
            self.assertFalse(self.driver.find_element_by_id(field).is_enabled())

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def logout(self):
        self.driver.delete_all_cookies()
        self.driver.get(self.base_url)

    def register(self, username, fullname, mail, password):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_link_text('Register').click()
        driver.find_element_by_id('field-username').clear()
        driver.find_element_by_id('field-username').send_keys(username)
        driver.find_element_by_id('field-fullname').clear()
        driver.find_element_by_id('field-fullname').send_keys(fullname)
        driver.find_element_by_id('field-email').clear()
        driver.find_element_by_id('field-email').send_keys(mail)
        driver.find_element_by_id('field-password').clear()
        driver.find_element_by_id('field-password').send_keys(password)
        driver.find_element_by_id('field-confirm-password').clear()
        driver.find_element_by_id('field-confirm-password').send_keys(password)
        driver.find_element_by_name('save').click()
        self.logout()

    def default_register(self, user):
        pwd = user.ljust(8, '0')
        self.register(user, user, '%s@conwet.com' % user, pwd)
        return pwd

    def login(self, username, password):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_link_text('Log in').click()
        driver.find_element_by_id('field-login').clear()
        driver.find_element_by_id('field-login').send_keys(username)
        driver.find_element_by_id('field-password').clear()
        driver.find_element_by_id('field-password').send_keys(password)
        driver.find_element_by_id('field-remember').click()
        driver.find_element_by_css_selector('button.btn.btn-primary').click()

    def create_organization(self, name, description):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_link_text('Organizations').click()
        driver.find_element_by_link_text('Add Organization').click()
        driver.find_element_by_id('field-name').clear()
        driver.find_element_by_id('field-name').send_keys(name)
        driver.find_element_by_id('field-description').clear()
        driver.find_element_by_id('field-description').send_keys(description)
        driver.find_element_by_name('save').click()

    def create_dataset(self, name, description, resource_url, resource_name, resource_description, resource_format):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_link_text('Datasets').click()
        driver.find_element_by_link_text('Add Dataset').click()

        # FIRST PAGE: Dataset properties
        driver.find_element_by_id('field-title').clear()
        driver.find_element_by_id('field-title').send_keys(name)
        driver.find_element_by_id('field-notes').clear()
        driver.find_element_by_id('field-notes').send_keys(description)

        driver.find_element_by_name('save').click()

        # SECOND PAGE: Add Resources
        try:
            # The link button is only clicked if it's present
            driver.find_element_by_link_text('Link').click()
        except Exception:
            pass

        driver.find_element_by_id('field-image-url').clear()
        driver.find_element_by_id('field-image-url').send_keys(resource_url)
        driver.find_element_by_id('field-name').clear()
        driver.find_element_by_id('field-name').send_keys(resource_name)
        driver.find_element_by_id('field-description').clear()
        driver.find_element_by_id('field-description').send_keys(resource_description)
        driver.find_element_by_id('s2id_autogen1').clear()
        driver.find_element_by_id('s2id_autogen1').send_keys(resource_format + '\n')
        driver.find_element_by_css_selector('button.btn.btn-primary').click()

    def complete_datarequest_form(self, title, description, organization_name=None):
        driver = self.driver

        driver.find_element_by_id('field-title').clear()
        driver.find_element_by_id('field-title').send_keys(title)
        driver.find_element_by_id('field-description').clear()
        driver.find_element_by_id('field-description').send_keys(description)

        if organization_name:
            Select(driver.find_element_by_xpath('//*[@id="field-organizations"]')).select_by_visible_text(organization_name)

        driver.find_element_by_name('save').click()

    def create_datarequest(self, title, description, organization_name=None):
        driver = self.driver

        driver.get(self.base_url)
        driver.find_element_by_xpath('//a[contains(@href, \'/datarequest\')]').click()
        driver.find_element_by_link_text('Add Data Request').click()

        self.complete_datarequest_form(title, description, organization_name)

        return driver.current_url.split('/')[-1]

    def edit_datarequest(self, datarequest_id, title, description):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)
        driver.find_element_by_link_text('Manage').click()
        self.complete_datarequest_form(title, description)

    def delete_datarequest(self, datarequest_id):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)

        driver.find_element_by_link_text('Manage').click()
        driver.find_element_by_link_text('Delete').click()
        driver.find_element_by_css_selector('div.modal-footer > button.btn.btn-primary').click()

    def close_datarequest(self, datarequest_id, dataset_name=None):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)

        driver.find_element_by_link_text('Close').click()

        if dataset_name:
            Select(driver.find_element_by_xpath('//*[@id="field-accepted_dataset_id"]')).select_by_visible_text(dataset_name)

        driver.find_element_by_name('close').click()

    def comment_datarequest(self, datarequest_id, comment):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/comment/' + datarequest_id)

        new_comment_form = driver.find_elements_by_name('comment')[-1]
        new_comment_form.clear()
        new_comment_form.send_keys(comment)

        driver.find_element_by_name('add').click()

    def edit_comment(self, datarequest_id, comment_pos, updated_comment):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/comment/' + datarequest_id)

        driver.find_elements(by=By.CSS_SELECTOR, value='i.fa-pencil')[comment_pos].click()
        driver.find_element_by_name('comment').clear()
        driver.find_element_by_name('comment').send_keys(updated_comment)
        driver.find_element_by_name('update').click()

    def check_datarequests_counter(self, n_datarequests, search=None):

        text = None

        if n_datarequests == 0:
            text = 'No data requests found'
        elif n_datarequests == 1:
            text = '1 data request found'
        else:
            text = '%d data requests found' % n_datarequests

        if search:
            text += ' for "%s"' % search

        self.assertEqual(text, self.driver.find_element_by_css_selector(".primary h2").text)

    def check_n_datarequests(self, expected_number):
        self.assertEqual(len(self.driver.find_elements_by_xpath(
                         '//li[@class=\'dataset-item\']')), expected_number)

    def check_datarequest(self, datarequest_id, title, description, open, owner,
                          organization='None', accepted_dataset='None'):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)

        self.assertEqual(title, driver.find_element_by_css_selector('h1.page-heading').text)
        self.assertEqual(description, driver.find_element_by_css_selector('p').text)

        self.assertEqual('OPEN' if open else 'CLOSED',
                         driver.find_element_by_xpath('//div[@id=\'content\']/div[3]/div/article/div/span').text)

        if open:
            self.assertEqual(owner, self.is_element_present(By.LINK_TEXT, 'Close'))

        self.assertEqual(organization, driver.find_element_by_xpath(
                         '//div[@id=\'content\']/div[3]/div/article/div/section/table/tbody/tr[2]/td').text)

        if not open:
            self.assertEqual(accepted_dataset, driver.find_element_by_xpath(
                             '//div[@id=\'content\']/div[3]/div/article/div/section/table/tbody/tr[5]/td').text)

        self.assertEqual(owner, self.is_element_present(By.LINK_TEXT, 'Manage'))

    def check_form_error(self, expected_message):
        self.assertEqual(expected_message, self.driver.find_element_by_xpath(
                         '//div[@id=\'content\']/div[3]/div/article/div/form/div/ul/li').text)

    def check_first_comment_text(self, expected_text):
        self.assertEqual(self.driver.find_element_by_xpath(
                         '//div[@class=\'comment-content \']').text,
                         expected_text)

    def check_element_optically_displayed(self, element):
        driver = self.driver
        scroll_top = driver.execute_script('return $(window).scrollTop()')
        scroll_bottom = driver.execute_script('return $(window).scrollTop() + $(window).height()')

        return element.location['y'] >= scroll_top and element.location['y'] <= scroll_bottom

    def test_create_datarequest_and_check_permissions(self):

        users = ['user1', 'user2']
        pwds = []

        # Create users
        for user in users:
            pwds.append(self.default_register(user))

        # The first user creates a data request and they are able to
        # close/modify it
        self.login(users[0], pwds[0])
        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)
        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, True, True)

        # Second user can access the data request but they are not able to
        # close/modify it
        self.logout()
        self.login(users[1], pwds[1])
        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, True, False)

        # Get user profile and check that user1 has one attached datarequest
        self.driver.get(self.base_url + 'user/datarequest/' + users[0])
        self.check_n_datarequests(1)
        self.check_datarequests_counter(1)
        self.driver.get(self.base_url + 'user/datarequest/' + users[1])
        self.check_n_datarequests(0)

    @parameterized.expand([
        ('', 0, 'Title: Title cannot be empty'),
        ('Title', 1001, 'Description: Description must be a maximum of 1000 characters long')
    ])
    def test_create_invalid_datarequest(self, title, description_length, expected_error):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        # Create the description
        description = _generate_random_string(description_length)

        # Check the returned error message
        self.create_datarequest(title, description)
        self.check_form_error(expected_error)

    def test_create_datarequest_same_name(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        # Create the comment
        title = 'Data Request'
        comment = 'Example description'

        # Create the datarequest
        self.create_datarequest(title, comment)

        # Create another data request with the same name (it should fail)
        self.create_datarequest(title, comment)
        self.check_form_error('Title: That title is already in use')

    @parameterized.expand([
        ('Cool DR', 10),
        ('', 10, 'Title: Title cannot be empty'),
        ('Updated Title', 1001, 'Description: Description must be a maximum of 1000 characters long')
    ])
    def test_update_datarequest(self, new_title, new_description_length, expected_error=None):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        # Create the data request
        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        new_description = _generate_random_string(new_description_length)

        # Update the data request
        self.edit_datarequest(datarequest_id, new_title, new_description)

        # If the data request is updated, we have to check the new status
        # Otherwise, we have to check if the error is arised
        if not expected_error:
            self.check_datarequest(datarequest_id, new_title, new_description, True, True)
        else:
            self.check_form_error(expected_error)

    def test_update_datarequest_same_name(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        # Create the comment
        title = 'Data Request'
        comment = 'Example description'

        # Create the first data request
        self.create_datarequest(title, comment)

        # Create the second data request
        second_dr_id = self.create_datarequest(title + 'a', comment)

        # Create another data request with the same name (it should fail)
        self.edit_datarequest(second_dr_id, title, comment)
        self.check_form_error('Title: That title is already in use')

    def test_delete_datarequest(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        # Create the data request
        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        # Delete the data request
        self.delete_datarequest(datarequest_id)

        # Check that there are not more data requests in the system
        self.assertTrue('No Data Requests found with the given criteria.'
                        in self.driver.find_element_by_css_selector('.primary p.empty').text)

        # Check flash message
        self.assertTrue('Data Request ' + datarequest_title + ' has been deleted'
                        in self.driver.find_element_by_xpath('//div[@id=\'content\']/div/div').text)

    def test_close_datarequest(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        # Create data request
        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        # Close data request
        self.close_datarequest(datarequest_id)

        # Check data request status
        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, False, True)

    @unittest.skipIf('.'.join(os.environ.get('CKANVERSION', '2.7').split('.')[:-1]) >= 2.8,
                     'This test cannot be run in CKAN >= 2.8 because elements in combo boxes cannot be selected')
    def test_close_datarequest_with_organization_and_accepted_dataset(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        organization_1_name = 'conwet'
        organization_2_name = 'upm'
        dataset_name = 'example'

        self.create_organization(organization_1_name, 'example description')
        self.create_organization(organization_2_name, 'example description')
        self.create_dataset(dataset_name, 'description', 'http://fiware.org',
                            'resource_name', 'resource_description', 'html')

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description,
                                                 organization_1_name)

        self.close_datarequest(datarequest_id, dataset_name)

        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, False, True,
                               organization_1_name, dataset_name)

        self.driver.get(self.base_url + 'datarequest')
        self.check_datarequests_counter(1)

        # Get organization and check that organization 1 has one attached datarequest
        self.driver.get(self.base_url + 'organization/datarequest/' + organization_1_name)
        self.check_n_datarequests(1)
        self.check_datarequests_counter(1)
        self.driver.get(self.base_url + 'organization/datarequest/' + organization_2_name)
        self.check_n_datarequests(0)
        self.check_datarequests_counter(0)

    def test_search_datarequests(self):

        def _check_pages(last_available):

            for i in range(1, last_available + 1):
                self.assertTrue(self.is_element_present(
                                By.LINK_TEXT, '{0}'.format(i)))

            self.assertFalse(self.is_element_present(
                             By.LINK_TEXT, '{0}'.format(last_available + 1)))

        user = 'user1'
        n_datarequests = 11
        base_name = 'Data Request'

        pwd = self.default_register(user)
        self.login(user, pwd)

        for i in range(n_datarequests):
            datarequest_title = '{0} {1}'.format(base_name, i)
            datarequest_description = 'Example Description'
            datarequest_id = self.create_datarequest(datarequest_title,
                                                     datarequest_description)

            if i % 2 == 0:
                self.close_datarequest(datarequest_id)

        # If ordered in ascending way, the first data request should be present
        # in the first page
        self.driver.get(self.base_url + 'datarequest')
        Select(self.driver.find_element_by_id('field-order-by')).select_by_visible_text('Oldest')
        self.assertTrue(self.is_element_present(By.LINK_TEXT, '{0} {1}'.format(base_name, 0)))
        self.check_datarequests_counter(n_datarequests)

        # There must be two pages (10 + 1). One page contains 10 items as a
        # maximum.
        _check_pages(2)
        self.check_n_datarequests(10)

        # The latest data request is in the second page
        self.driver.find_element_by_link_text('2').click()
        self.assertTrue(self.is_element_present(By.LINK_TEXT, '{0} {1}'.format(base_name, n_datarequests - 1)))
        self.check_n_datarequests(1)

        for i in range(n_datarequests):
            datarequest_title = 'test {0}'.format(i)
            datarequest_description = 'Example Description'
            datarequest_id = self.create_datarequest(datarequest_title,
                                                     datarequest_description)

        self.driver.get(self.base_url + 'datarequest')

        # There must be three pages (10 + 10 + 2). One page contains 10 items
        # as a maximum.
        _check_pages(3)
        self.check_n_datarequests(10)
        self.check_datarequests_counter(n_datarequests * 2)

        # Search by base name
        self.driver.find_element_by_xpath('(//input[@name=\'q\'])[2]').clear()
        self.driver.find_element_by_xpath('(//input[@name=\'q\'])[2]').send_keys(base_name)
        self.driver.find_element_by_xpath('//button[@value=\'search\']').click()

        # There should be two pages
        _check_pages(2)
        self.check_n_datarequests(10)
        self.check_datarequests_counter(n_datarequests, base_name)

        # Filter by open (there should be 5 data requests open with the given
        # base name)
        self.driver.find_element_by_partial_link_text('Open').click()
        self.check_n_datarequests(5)
        self.check_datarequests_counter(5, base_name)

        # Pages selector is not available when there are less than 10 items
        self.assertFalse(self.is_element_present(By.LINK_TEXT, '1'))

    def test_create_comment_and_check_permissions(self):

        def _check_is_editable(editable):
            self.assertEqual(editable, self.is_element_present(By.CSS_SELECTOR, 'i.fa-pencil'))
            self.assertEqual(editable, self.is_element_present(By.CSS_SELECTOR, 'i.fa-times'))

        users = ['user1', 'user2']
        pwds = []

        # Create users
        for user in users:
            pwds.append(self.default_register(user))

        # First user creates the data request
        self.login(users[0], pwds[0])
        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        # Second user creates the comment so they are able to modify it
        self.logout()
        self.login(users[1], pwds[1])

        comment = 'this is a sample comment'
        self.comment_datarequest(datarequest_id, comment)

        _check_is_editable(True)
        self.check_first_comment_text(comment)

        # First user is not able to modify the comment
        self.logout()
        self.login(users[0], pwds[0])

        self.driver.get(self.base_url + 'datarequest/comment/' +
                        datarequest_id)

        _check_is_editable(False)
        self.check_first_comment_text(comment)

    @parameterized.expand([
        (),
        (1001, 'Comment: Comments must be a maximum of 1000 characters long')
    ])
    def test_update_comment(self, comment_length=10, expected_error=None):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        comment = 'this is a sample comment'
        self.comment_datarequest(datarequest_id, comment)

        updated_comment = _generate_random_string(comment_length)
        self.edit_comment(datarequest_id, 0, updated_comment)

        if not expected_error:
            # Check that the comment has been updated appropriately
            self.check_first_comment_text(updated_comment)
        else:
            # Check the error
            self.assertEqual(expected_error, self.driver.find_element_by_xpath(
                             '//div[@id=\'content\']/div[3]/div/article/div/div/div/form/div/ul/li').text)

    def test_delete_comment(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        self.comment_datarequest(datarequest_id, 'sample comment')

        # Delete the comment
        self.driver.find_element_by_css_selector('i.fa-times').click()
        self.driver.find_element_by_css_selector('.modal-footer > button.btn.btn-primary').click()

        # Check that the comment has been deleted
        self.assertEqual('This data request has not been commented yet',
                         self.driver.find_element_by_css_selector('p.empty').text)
        self.assertTrue('Comment has been deleted' in self.driver.find_element_by_xpath(
                        '//div[@id=\'content\']/div/div').text)

    def test_new_comments_always_visible(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        for i in range(10):
            self.comment_datarequest(datarequest_id, 'comment {0}'.format(i))

            # Last comment should be always visible
            comments = self.driver.find_elements_by_xpath('//div[@class=\'comment-content \']')
            self.assertTrue(self.check_element_optically_displayed(comments[-1]))

        # After creating ten comments, the first one should not be visible
        self.assertFalse(self.check_element_optically_displayed(comments[0]))

    def test_create_invalid_comment(self):

        user = 'user1'

        pwd = self.default_register(user)
        self.login(user, pwd)

        # Create Data Request
        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        # Check that an error is raised
        comment = _generate_random_string(1001)
        self.comment_datarequest(datarequest_id, comment)
        self.assertEqual('Comment: Comments must be a maximum of 1000 characters long',
                         self.driver.find_element_by_xpath('//form[@id=\'comment-form\']/div[2]/ul/li').text)
