"""
Main file containing tests for unit tests and continuous integration.
https://docs.djangoproject.com/en/3.1/topics/testing/tools/
"""

from django.test import TestCase, Client
from django.contrib import auth

from .models import CustomUser


class TestAuth(TestCase):
    """
    Tests the login/registration pages and forms.
    """

    def setUp(self):
        """
        Setup func that is called before each test.
        """

        # create dummy user
        self.credentials = {
            'username': 'test_user',
            'password': 'test_password'
        }
        self.test_user = CustomUser.objects.create_user(**self.credentials)
        self.test_user.save()

        # create test client
        self.client = Client()

    def test_load_login(self):
        """
        Tests loading the login page.
        """

        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_load_registration(self):
        """
        Tests loading the registration page.
        """

        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_submit_login_form_fail(self):
        """
        Tests submitting a login form with invalid credentials.
        """

        # submit some invalid credentials
        response = self.client.post(
            path='/login',
            data={
                'username': 'bad_user',
                'password': 'bad_password'
            }
        )

        # validate that user is not logged in and given an error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_submit_login_form_success(self):
        """
        Tests submitting a login form with valid credentials.
        """

        # submit a login form with valid credentials
        response = self.client.post(
            path='/login',
            data={**self.credentials},
            follow=True
        )

        # validate the user is logged in and redirected to homepage
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertNotContains(response, "Invalid username or password.")
        self.assertRedirects(response, '/')

    def test_logout(self):
        """
        Tests the logout of a user.
        """

        # login a user for testing
        self.client.login(**self.credentials)

        # call logout
        response = self.client.get('/logout', follow=True)

        # validate that the user was in-fact, logged out
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # validate that the user was redirect to the login page with a success message
        self.assertRedirects(response, '/login')
        self.assertContains(response, 'Successfully logged out!')

    def test_registration_success(self):
        """
        Tests successfully registering a new user.
        """

        # submit register form with new credentials
        response = self.client.post(
            path='/register',
            data={
                'username': 'some_user',
                'password': 'some_password',
                're_password': 'some_password'
            },
            follow=True
        )

        # validate the user is logged in and redirected to the homepage (inbox)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, '/')

        # validate that the user object was created
        self.assertIsNotNone(CustomUser.objects.get(username='some_user'))

    def test_registration_fail(self):
        """
        Tests unsuccessfully registering a new user.
        """

        # submit an invalid, already existing credential
        response = self.client.post(
            path='/register',
            data={
                'username': self.credentials['username'],
                'password': self.credentials['password'],
                're_password': self.credentials['password']
            }
        )

        # validate that it rejects and gives error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.')
        self.assertFalse(response.context['user'].is_authenticated)


class TestInbox(TestCase):
    """
    Tests the main inbox functionality of the website.
    """

    # TODO: add tests for inbox
