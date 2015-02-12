#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import urllib2

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from pages.page import Page


class CrashStatsBasePage(Page):

    _page_heading_locator = (By.CSS_SELECTOR, 'div.page-heading > h2')
    _server_status_locator = (By.LINK_TEXT, 'Server Status')
    _link_to_bugzilla_locator = (By.CSS_SELECTOR, '.panel a')

    @property
    def page_title(self):
        WebDriverWait(self.selenium, self.timeout).until(lambda s: self.selenium.title)
        return self.selenium.title

    @property
    def page_heading(self):
        return self.selenium.find_element(*self._page_heading_locator).text

    def click_server_status(self):
        self.selenium.find_element(*self._server_status_locator).click()
        from pages.status_page import CrashStatsStatus
        return CrashStatsStatus(self.testsetup)

    def get_random_indexes(self, item_list, max_indexes, start=0, end=-1):
        """
            Return a list of random indexes for a list of items
            max_indexes is maximum # of indexes to return
            'start' is start of index range, defaults to zero
            'end' is end of index range, as used by range( ), defaults to length of item_list
        """
        import random
        if end < 0:
            end = len(item_list)
        return [random.randrange(start, end) for _ in range(0, min(max_indexes, len(item_list)))]

    @property
    def link_to_bugzilla(self):
        return self.selenium.find_element(*self._link_to_bugzilla_locator).get_attribute('href')

    @property
    def header(self):
        return self.Header(self.testsetup)

    @property
    def footer(self):
        return self.Footer(self.testsetup)

    class Header(Page):

        _find_crash_id_or_signature = (By.ID, 'q')
        _product_select_locator = (By.ID, 'products_select')
        _report_select_locator = (By.ID, 'report_select')
        _all_versions_locator = (By.ID, 'product_version_select')
        _current_versions_locator = (By.CSS_SELECTOR, 'optgroup:nth-of-type(2) option')
        _other_versions_locator = (By.CSS_SELECTOR, 'optgroup:nth-of-type(3) option')
        _versions_locator = (By.TAG_NAME, 'option')
        _loader_locator = (By.CLASS_NAME, 'loader')

        _exploitable_crash_report_locator = (By.CSS_SELECTOR, '#report_select option[value="/report/exploitability/"]')
        _super_search_locator = (By.LINK_TEXT, 'Super Search')

        @property
        def current_product(self):
            element = self.selenium.find_element(*self._product_select_locator)
            select = Select(element)
            return select.first_selected_option.text

        @property
        def current_version(self):
            element = self.selenium.find_element(*self._all_versions_locator)
            select = Select(element)
            return select.first_selected_option.text

        @property
        def current_versions(self):
            from pages.version import FirefoxVersion
            current_versions = []
            for element in self.selenium.find_element(*self._all_versions_locator).find_elements(*self._current_versions_locator):
                str(current_versions.append(FirefoxVersion(element.text)))
            return current_versions

        @property
        def other_versions(self):
            from pages.version import FirefoxVersion
            other_versions = []
            for element in self.selenium.find_element(*self._all_versions_locator).find_elements(*self._other_versions_locator):
                str(other_versions.append(FirefoxVersion(element.text)))
            return other_versions

        @property
        def version_select_text(self):
            '''
                Return the text in the Version selector
            '''
            versions = []
            for element in self.selenium.find_element(*self._all_versions_locator).find_elements(*self._versions_locator):
                versions.append(element.text)
            return versions

        @property
        def current_report(self):
            element = self.selenium.find_element(*self._report_select_locator)
            select = Select(element)
            return select.first_selected_option.text

        @property
        def product_list(self):
            element = self.selenium.find_element(*self._product_select_locator)
            return [option.text for option in Select(element).options]

        def select_product(self, application):
            '''
                Select the Mozilla Product you want to report on
            '''
            element = self.selenium.find_element(*self._product_select_locator)
            select = Select(element)
            return select.select_by_visible_text(application)

        def select_version(self, version):
            '''
                Select the version of the application you want to report on
            '''
            version_dropdown = self.selenium.find_element(*self._all_versions_locator)
            select = Select(version_dropdown)
            select.select_by_visible_text(str(version))

        def select_version_by_index(self, index):
            '''
                Select the version of the application you want to report on
            '''
            version_dropdown = self.selenium.find_element(*self._all_versions_locator)
            select = Select(version_dropdown)
            select.select_by_index(index)

        def select_report(self, report_name):
            '''
                Select the report type from the drop down
                and wait for the page to reload
            '''
            report_dropdown = self.selenium.find_element(*self._report_select_locator)
            select = Select(report_dropdown)
            select.select_by_visible_text(report_name)

            if 'Top Crashers' == report_name:
                from pages.crash_stats_top_crashers_page import CrashStatsTopCrashers
                return CrashStatsTopCrashers(self.testsetup)
            elif 'Top Crashers by TopSite' == report_name:
                from pages.crash_stats_top_crashers_by_site_page import CrashStatsTopCrashersBySite
                return CrashStatsTopCrashersBySite(self.testsetup)
            elif 'Crashes per User' == report_name:
                from pages.crash_stats_per_active_daily_user_page import CrashStatsPerActiveDailyUser
                return CrashStatsPerActiveDailyUser(self.testsetup)
            elif 'Nightly Builds' == report_name:
                from pages.crash_stats_nightly_builds_page import CrashStatsNightlyBuilds
                return CrashStatsNightlyBuilds(self.testsetup)
            elif 'Top Changers' == report_name:
                from pages.crash_stats_top_changers_page import CrashStatsTopChangers
                return CrashStatsTopChangers(self.testsetup)

        def search_for_crash(self, crash_id_or_signature):
            '''
                Type the signature or the id of a bug into the search bar and submit the form
            '''
            search_box = self.selenium.find_element(*self._find_crash_id_or_signature)
            # explicitly only testing search and not the onfocus event which clears the
            # search field
            search_box.clear()
            search_box.send_keys(crash_id_or_signature)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(self.selenium, self.timeout).until(lambda s: not self.is_element_present(*self._loader_locator))

            from pages.super_search_page import CrashStatsSuperSearch
            return CrashStatsSuperSearch(self.testsetup)

        @property
        def report_list(self):
            report_dropdown = self.selenium.find_element(*self._report_select_locator)
            select = Select(report_dropdown)
            return [opt.text for opt in select.options]

        @property
        def is_exploitable_crash_report_present(self):
            return self.is_element_present(*self._exploitable_crash_report_locator)

        def click_super_search(self):
            self.selenium.find_element(*self._super_search_locator).click()
            from pages.super_search_page import CrashStatsSuperSearch
            return CrashStatsSuperSearch(self.testsetup)

    class Footer(Page):

        _browserid_login_locator = (By.CSS_SELECTOR, 'div.login a.browserid-login')
        _browserid_logout_locator = (By.CSS_SELECTOR, 'div.login a.browserid-logout')

        @property
        def is_logged_out(self):
            return self.selenium.find_element(*self._browserid_login_locator).is_displayed()

        @property
        def is_logged_in(self):
            return self.selenium.find_element(*self._browserid_logout_locator).is_displayed()

        def login(self, email=None, password=None):
            '''
                Login using persona - if no email is specified a one time set of
                verified persona credentials, email and password, are generated
                and used.
                :param email: verified BrowserID email
                :param password: BrowserID password
            '''
            if email is None:
                credentials = self.get_new_persona_credentials()
                email = credentials['email']
                password = credentials['password']

            self.selenium.find_element(*self._browserid_login_locator).click()

            from browserid import BrowserID
            pop_up = BrowserID(self.selenium, self.timeout)
            pop_up.sign_in(email, password)
            WebDriverWait(self.selenium, self.timeout).until(
                lambda s: self.is_logged_in, message='Could not log in within %s seconds.' % self.timeout)

        def logout(self):
            self.selenium.find_element(*self._browserid_logout_locator).click()
            WebDriverWait(self.selenium, self.timeout).until(
                lambda s: self.is_logged_out, message='Could not log out within %s seconds.' % self.timeout)

        def get_new_persona_credentials(self):
            url = "http://personatestuser.org/email/"
            response = urllib2.urlopen(url).read()
            decode = json.loads(response)
            credentials = {
                'email': decode['email'],
                'password': decode['pass']
            }
            return credentials
