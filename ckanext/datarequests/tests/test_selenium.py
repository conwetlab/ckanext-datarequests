# -*- coding: utf-8 -*-

# Copyright (c) 2014 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of CKAN Private Dataset Extension.

# CKAN Private Dataset Extension is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CKAN Private Dataset Extension is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with CKAN Private Dataset Extension.  If not, see <http://www.gnu.org/licenses/>.

from nose_parameterized import parameterized
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from subprocess import Popen

import ckan.lib.search.index as search_index
import ckan.model as model
import ckanext.datarequests.db as db
import json
import os
import unittest
import re
import requests


def normalize_title(title):
    return title.replace(' ', '-').lower()


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
        self.register(user, user, '%s@conwet.com' % user, user)

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

        driver.find_element_by_id("field-title").clear()
        driver.find_element_by_id("field-title").send_keys(title)
        driver.find_element_by_id("field-description").clear()
        driver.find_element_by_id("field-description").send_keys(description)

        if organization_name:
            Select(driver.find_element_by_id('field-organizations')).select_by_visible_text(organization_name)

        driver.find_element_by_name("save").click()

    def create_datarequest(self, title, description, organization_name=None):
        driver = self.driver

        driver.get(self.base_url)
        driver.find_element_by_xpath("//a[contains(@href, '/datarequest')]").click()
        driver.find_element_by_link_text("Add Data Request").click()

        self.complete_datarequest_form(title, description, organization_name)

        return driver.current_url.split('/')[-1]

    def edit_datarequest(self, datarequest_id, title, description):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)
        driver.find_element_by_link_text("Manage").click()
        self.complete_datarequest_form(title, description)

    def delete_datarequest(self, datarequest_id):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)

        driver.find_element_by_link_text("Manage").click()
        driver.find_element_by_link_text("Delete").click()
        driver.find_element_by_css_selector("div.modal-footer > button.btn.btn-primary").click()

    def close_datarequest(self, datarequest_id, dataset_name=None):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)

        driver.find_element_by_link_text("Close").click()

        if dataset_name:
            Select(driver.find_element_by_id('field-accepted_dataset_id')).select_by_visible_text(dataset_name)

        driver.find_element_by_name("close").click()

    def check_datarequest(self, datarequest_id, title, description, open, owner, 
                          organization="None", accepted_dataset="None"):
        driver = self.driver
        driver.get(self.base_url + 'datarequest/' + datarequest_id)

        self.assertEqual(title, driver.find_element_by_css_selector("h1.page-heading").text)
        self.assertEqual(description, driver.find_element_by_css_selector("p").text)

        self.assertEqual("OPEN" if open else "CLOSED",
                         driver.find_element_by_xpath("//div[@id='content']/div[3]/div/article/div/span").text)

        if open:
            self.assertEqual(owner, self.is_element_present(By.LINK_TEXT, "Close"))

        self.assertEqual(organization, driver.find_element_by_xpath(
                         "//div[@id='content']/div[3]/div/article/div/section/table/tbody/tr[2]/td").text)

        if not open:
            self.assertEqual(accepted_dataset, driver.find_element_by_xpath(
                             "//div[@id='content']/div[3]/div/article/div/section/table/tbody/tr[5]/td").text)

        self.assertEqual(owner, self.is_element_present(By.LINK_TEXT, "Manage"))

    def test_create_and_permissions(self):

        users = ['user1', 'user2']

        # Create users
        for user in users:
            self.default_register(user)

        # The first user creates a data request and they are able to
        # close/modify it
        self.login(users[0], users[0])
        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)
        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, True, True)

        # Second user can access the data request but they are not able to
        # close/modify it
        self.logout()
        self.login(users[1], users[1])
        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, True, False)

    def test_update(self):

        user = 'user1'

        self.default_register(user)
        self.login(user, user)

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        datarequest_modified_title = 'Cool DR'
        datarequest_modified_description = 'I want all the data coming from Santander'

        self.edit_datarequest(datarequest_id, datarequest_modified_title,
                              datarequest_modified_description)

        self.check_datarequest(datarequest_id, datarequest_modified_title,
                               datarequest_modified_description, True, True)

    def test_delete(self):

        user = 'user1'

        self.default_register(user)
        self.login(user, user)

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        self.delete_datarequest(datarequest_id)

        self.assertTrue("There are currently no Data Requests for this site."
                        in self.driver.find_element_by_css_selector("p.empty").text)

        self.assertTrue("Your Data Request " + datarequest_title + " has been deleted"
                        in self.driver.find_element_by_xpath("//div[@id='content']/div/div").text)

    def test_close(self):

        user = 'user1'

        self.default_register(user)
        self.login(user, user)

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description)

        self.close_datarequest(datarequest_id)

        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, False, True)

    def test_close_with_organization_and_accepted_dataset(self):

        user = 'user1'

        self.default_register(user)
        self.login(user, user)

        organization_name = 'conwet'
        dataset_name = 'example'

        self.create_organization(organization_name, 'example description')
        self.create_dataset(dataset_name, 'description', 'http://fiware.org',
                            'resource_name', 'resource_description', 'html')

        datarequest_title = 'Data Request 1'
        datarequest_description = 'Example Description'
        datarequest_id = self.create_datarequest(datarequest_title,
                                                 datarequest_description,
                                                 organization_name)

        self.close_datarequest(datarequest_id, dataset_name)

        self.check_datarequest(datarequest_id, datarequest_title,
                               datarequest_description, False, True,
                               organization_name, dataset_name)

    def test_search(self):

        def _check_pages(last_available):

            for i in range(1, last_available + 1):
                self.assertTrue(self.is_element_present(
                                By.LINK_TEXT, "{0}".format(i)))

            self.assertFalse(self.is_element_present(
                             By.LINK_TEXT, "{0}".format(last_available + 1)))

        def _check_n_datarequests(expected_number):
            self.assertEqual(len(self.driver.find_elements_by_xpath(
                             "//li[@class='dataset-item']")), expected_number)

        user = 'user1'
        n_datarequests = 11
        base_name = 'Data Request'

        self.default_register(user)
        self.login(user, user)

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
        Select(self.driver.find_element_by_id("field-order-by")).select_by_visible_text("Oldest")
        self.assertTrue(self.is_element_present(By.LINK_TEXT, '{0} {1}'.format(base_name, 0)))

        # There must be two pages (10 + 1). One page contains 10 items as a
        # maximum.
        _check_pages(2)
        _check_n_datarequests(10)

        # The latest data request is in the second page
        self.driver.find_element_by_link_text("2").click()
        self.assertTrue(self.is_element_present(By.LINK_TEXT, '{0} {1}'.format(base_name, n_datarequests - 1)))

        for i in range(n_datarequests):
            datarequest_title = 'test {0}'.format(i)
            datarequest_description = 'Example Description'
            datarequest_id = self.create_datarequest(datarequest_title,
                                                     datarequest_description)

        self.driver.get(self.base_url + 'datarequest')

        # There must be three pages (10 + 10 + 2). One page contains 10 items
        # as a maximum.
        _check_pages(3)
        _check_n_datarequests(10)

        # Search by base name
        self.driver.find_element_by_xpath("(//input[@name='q'])[2]").clear()
        self.driver.find_element_by_xpath("(//input[@name='q'])[2]").send_keys(base_name)
        self.driver.find_element_by_xpath("//button[@value='search']").click()

        # There should be two pages
        _check_pages(2)
        _check_n_datarequests(10)

        # Filter by open (there should be 5 data requests open with the given
        # base name)
        self.driver.find_element_by_link_text("Open (5)").click()
        _check_n_datarequests(5)

        # Pages selector is not available when there are less than 10 items
        self.assertFalse(self.is_element_present(By.LINK_TEXT, "1"))
