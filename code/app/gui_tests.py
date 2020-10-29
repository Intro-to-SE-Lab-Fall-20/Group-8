"""
Main file containing tests for unit testing and continuous integration.
https://docs.djangoproject.com/en/3.1/topics/testing/tools/
"""

from selenium import webdriver
import docker
import time


from django.test import TestCase, Client
from django.contrib import auth
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from .models import CustomUser, Email, Sender, Recipient, Attachment


def create_email(subject, content, sender, recipients, is_draft, is_forward):
    """
    Helper function for setting up the DB for testing.
    Creates an Email instance along with respective Sender and Recipient relations.
    """

    # create email object
    email = Email.objects.create(
        body=content,
        subject=subject
    )

    # create sender object
    sender_relation = Sender.objects.create(
        user=sender,
        email=email,
        is_draft=is_draft,
        is_forward=is_forward
    )

    # create recipients objects
    recipient_relations = []
    for recipient in recipients:
        recipient_relations.append(
            Recipient.objects.create(
                user=recipient,
                email=email,
                is_sent=not is_draft,
                is_forward=is_forward
            )
        )

    return email, sender_relation, recipient_relations


class TestAuthGui(StaticLiveServerTestCase):
    """
    A collection of GUI tests for the sites auth functionality.
    """

    def setUp(self):
        super().setUp()
        self.driver = webdriver.Firefox()

        # create a dummy test user
        self.credentials = {
            'username': 'test_user',
            'password': 'test_password'
        }
        self.test_user = CustomUser.objects.create_user(**self.credentials)

    def tearDown(self):
        self.driver.quit()
        super().tearDown()

    def test_login_success(self):
        """
        Tests a successful login.
        """

        # load the login page
        self.driver.get(self.live_server_url)
        assert "Login" in self.driver.title

        # enter some login info and submit
        username_element = self.driver.find_element_by_id('inputUsername')
        username_element.send_keys(self.credentials['username'])
        password_element = self.driver.find_element_by_id('inputPassword')
        password_element.send_keys(self.credentials['password'])
        submit_btn = self.driver.find_element_by_class_name('btn-block')
        submit_btn.click()
        self.driver.implicitly_wait(3)

        # verify we're redirect to the user's inbox
        assert "Inbox" in self.driver.title

        # verify success message is displayed
        alert_msg = self.driver.find_element_by_class_name('ajs-success')
        assert f"Welcome back {self.credentials['username']}!" in alert_msg.get_attribute('innerHTML')

    def test_login_failure(self):
        """
        Tests a failed login attempt.
        """

        # load the login page
        self.driver.get(self.live_server_url)
        assert "Login" in self.driver.title

        # enter invalid username and submit
        username_element = self.driver.find_element_by_id('inputUsername')
        username_element.send_keys('bad_username')
        password_element = self.driver.find_element_by_id('inputPassword')
        password_element.send_keys('bad_password')
        submit_btn = self.driver.find_element_by_class_name('btn-block')
        submit_btn.click()
        self.driver.implicitly_wait(3)

        # verify we're NOT redirected to inbox
        assert "Login" in self.driver.title

        # verify warning message is displayed
        warn_msg = self.driver.find_element_by_class_name('ajs-warning')
        assert "Invalid username or password." == warn_msg.get_attribute('innerHTML')

        # enter valid username with invalid password and submit
        username_element = self.driver.find_element_by_id('inputUsername')
        username_element.send_keys(self.credentials['username'])
        password_element = self.driver.find_element_by_id('inputPassword')
        password_element.send_keys('bad_password')
        submit_btn = self.driver.find_element_by_class_name('btn-block')
        submit_btn.click()
        self.driver.implicitly_wait(3)

        # verify we're NOT redirected to inbox
        assert "Login" in self.driver.title

        # verify warning message is displayed
        warn_msg = self.driver.find_element_by_class_name('ajs-warning')
        assert "Invalid username or password." == warn_msg.get_attribute('innerHTML')

    def test_register_success(self):
        """
        Tests a successful registration attempt.
        """

        new_creds = {
            'username': 'new_user',
            'password': 'new_password'
        }

        # load the registration page
        self.driver.get(self.live_server_url + "/register")
        assert "Register" in self.driver.title

        # enter new valid username and password
        username_element = self.driver.find_element_by_name('username')
        username_element.send_keys(new_creds['username'])
        password_element = self.driver.find_element_by_name('password')
        password_element.send_keys(new_creds['password'])
        repassword_element = self.driver.find_element_by_name('re_password')
        repassword_element.send_keys(new_creds['password'])
        submit_btn = self.driver.find_element_by_class_name('btn-block')
        submit_btn.click()
        self.driver.implicitly_wait(3)

        # verify redirect to inbox
        assert "Inbox" in self.driver.title

        # verify success message is displayed
        succ_msg = self.driver.find_element_by_class_name('ajs-success')
        assert f"Welcome {new_creds['username']}!" == succ_msg.get_attribute('innerHTML')

    def test_register_failure(self):
        """
        Tests a failed registration attempt.
        """

        new_creds = {
            'username': 'test_user',
            'password': 'new_password'
        }

        # load the registration page
        self.driver.get(self.live_server_url + "/register")
        assert "Register" in self.driver.title

        # enter new valid username and password
        username_element = self.driver.find_element_by_name('username')
        username_element.send_keys(new_creds['username'])
        password_element = self.driver.find_element_by_name('password')
        password_element.send_keys(new_creds['password'])
        repassword_element = self.driver.find_element_by_name('re_password')
        repassword_element.send_keys(new_creds['password'])
        submit_btn = self.driver.find_element_by_class_name('btn-block')
        submit_btn.click()
        self.driver.implicitly_wait(3)

        # verify this does NOT redirect to inbox
        assert "Register" in self.driver.title

        # verify warning message is displayed
        warn_msg = self.driver.find_element_by_class_name('ajs-error')
        assert "A user with that username already exists." == warn_msg.get_attribute('innerHTML')
