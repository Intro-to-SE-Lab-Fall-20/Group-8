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
        self.assertEqual(response.status_code, 404)

    def test_submit_bad_login_form(self):
        """
        Tests submitting a login form with invalid credentials.
        """

        response = self.client.post(
            path='/login',
            data={
                'username': 'bad_user',
                'password': 'bad_password'
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_submit_good_login_form(self):
        """
        Tests submitting a login form with valid credentials.
        """

        response = self.client.post(
            path='/login',
            data={**self.credentials},
            follow=True
        )

        self.assertTrue(response.context['user'].is_authenticated)
        self.assertNotContains(response, "Invalid username or password.")
        self.assertRedirects(response, '/')

    def test_logout(self):
        """
        Tests the logout of a user.
        """

        self.client.login(**self.credentials)

        response = self.client.get('/logout', follow=True)

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.assertRedirects(response, '/login')
        self.assertContains(response, 'Successfully logged out!')


class TestInbox(TestCase):
    """
    Tests the main inbox functionality of the website.
    """

    # TODO: add tests for inbox
