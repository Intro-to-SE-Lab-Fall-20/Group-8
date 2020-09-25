"""
Main file containing tests for unit tests and continuous integration.
https://docs.djangoproject.com/en/3.1/topics/testing/tools/
"""

from django.test import TestCase, Client
from django.contrib import auth

from .models import CustomUser, Email, Sender, Recipient


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
        self.assertContains(response, f'Welcome back {self.credentials["username"]}!')
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
        self.assertContains(response, f'See ya later {self.credentials["username"]}!')

    def test_registration_success(self):
        """
        Tests successfully registering a new user.
        """

        new_credentials = {
            'username': 'some_user',
            'password': 'some_password',
            're_password': 'some_password'
        }

        # submit register form with new credentials
        response = self.client.post(
            path='/register',
            data=new_credentials,
            follow=True
        )

        # validate the user is logged in and redirected to the homepage (inbox)
        self.assertContains(response, f'Welcome {new_credentials["username"]}!')
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
            data=self.credentials
        )

        # validate that it rejects and gives error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists.')
        self.assertFalse(response.context['user'].is_authenticated)


class TestCompose(TestCase):
    """
    Tests the compose functionality of the website.
    """

    def setUp(self):
        """
        Sets up some prerequisites before each test.
        """

        # create sender user
        self.credentials = {
            'username': 'test_user',
            'password': 'test_password'
        }
        self.sender = CustomUser.objects.create_user(**self.credentials, email="test_user@email.com")

        # create test client and log in as sender user
        self.client = Client()
        self.client.login(**self.credentials)

        # create some recipient users
        self.recipients = [
            CustomUser.objects.create_user(
                username="recipient_one",
                password="recipient_one",
                email="recipient_one@email.com"
            ),
            CustomUser.objects.create_user(
                username="recipient_two",
                password="recipient_two",
                email="recipient_two@email.com"
            )
        ]

    def test_load_compose(self):
        """
        Tests if the compose.html page loads.
        """

        response = self.client.get('/compose')

        self.assertEqual(response.status_code, 200)

    def test_compose_success(self):
        """
        Tests submitting a compose form with valid inputs.
        """

        # build some valid form data
        form_data = {
            'subject': 'This is a good subject',
            'sender': f"{self.sender.email}",
            'recipients': ''.join(f"{user.email}," for user in self.recipients),
            'body': 'This is a valid body',
            'is_draft': 'false',
            'is_forward': 'false'
        }

        # submit compose form
        response = self.client.post(
            path='/compose',
            data=form_data,
            follow=True
        )

        # validate form was submitted successfully
        self.assertContains(response, f'Message sent!')
        self.assertRedirects(response, '/')

        # grab Sender and Email objects from DB
        sender = Sender.objects.get(user=self.sender)
        email = Email.objects.get(sender_email=sender)

        # validate Sender
        self.assertFalse(sender.is_draft)
        self.assertFalse(sender.is_forward)
        self.assertEqual(sender.email, email)

        # validate Email
        self.assertEqual(email.body, form_data['body'])
        self.assertEqual(email.subject, form_data['subject'])

        # validate Recipients
        for recipient_user in self.recipients:
            recipient = Recipient.objects.get(user=recipient_user)
            self.assertEqual(recipient.email, email)
            self.assertTrue(recipient.is_sent)
            self.assertFalse(recipient.is_read)
            self.assertFalse(recipient.is_forward)
            self.assertFalse(recipient.is_archived)

    def test_compose_invalid_subject(self):
        """
        Tests submitting a compose form with an invalid subject.
        """

        # build some valid form data
        form_data = {
            'subject': '',
            'sender': f"{self.sender.email}",
            'recipients': ''.join(f"{user.email}," for user in self.recipients),
            'body': 'This is a valid body',
            'is_draft': 'false',
            'is_forward': 'false'
        }

        # submit compose form
        response = self.client.post(
            path='/compose',
            data=form_data,
            follow=True
        )

        # validate form was submitted successfully
        self.assertContains(response, f'Invalid subject: subject cannot be empty!')
        self.assertEqual(response.status_code, 200)

        # make sure that no objects were actually created in the db
        self.assertEqual(Email.objects.all().count(), 0)
        self.assertEqual(Sender.objects.all().count(), 0)
        self.assertEqual(Recipient.objects.all().count(), 0)

    def test_compose_invalid_recipient(self):
        """
        Tests submitting a compose form with an invalid recipient.
        """

        # build some valid form data
        form_data = {
            'subject': '',
            'sender': f"{self.sender.email}",
            'recipients': 'invalid_recipient',
            'body': 'This is a valid body',
            'is_draft': 'false',
            'is_forward': 'false'
        }

        # submit compose form
        response = self.client.post(
            path='/compose',
            data=form_data,
            follow=True
        )

        # validate form was submitted successfully
        self.assertContains(response, f'Invalid recipients: one of your recipients was not found!')
        self.assertEqual(response.status_code, 200)

        # make sure that no objects were actually created in the db
        self.assertEqual(Email.objects.all().count(), 0)
        self.assertEqual(Sender.objects.all().count(), 0)
        self.assertEqual(Recipient.objects.all().count(), 0)


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


class TestInbox(TestCase):
    """
    Tests the main inbox functionality of the website.
    """

    def setUp(self):
        """
        Sets up some prerequisites before each test.
        """

        # create dummy user
        self.credentials = {
            'username': 'test_user',
            'password': 'test_password'
        }
        self.test_user = CustomUser.objects.create_user(**self.credentials)

        # create test client and log in the user
        self.client = Client()
        self.client.login(**self.credentials)

        # create a test sender user
        self.sender = CustomUser.objects.create_user(
            username="recipient_one",
            password="recipient_one",
            email="recipient_one@email.com"
        )

    def test_load_inbox(self):
        """
        Tests that the inbox.html page loads.
        """

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_inbox_received_emails(self):
        """
        Tests that the inbox view correctly displays emails received by a user.
        """

        # create some test emails
        create_email(
            subject='Testing subject',
            content='Testing content',
            sender=self.sender,
            recipients=[self.test_user],
            is_draft=False,
            is_forward=False
        )
        create_email(
            subject='Another subject',
            content='Even more content',
            sender=self.sender,
            recipients=[self.test_user],
            is_draft=False,
            is_forward=False
        )

        # check that the inbox renders this email correctly
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 2)

    def test_inbox_not_received_emails(self):
        """
        Tests that the inbox view does NOT display emails that have not been sent yet.
        """

        # create a test email
        create_email(
            subject='Testing subject',
            content='Testing content',
            sender=self.sender,
            recipients=[self.test_user],
            is_draft=True,
            is_forward=False
        )
        create_email(
            subject='Another subject',
            content='Even more content',
            sender=self.sender,
            recipients=[self.test_user],
            is_draft=True,
            is_forward=False
        )

        # check that the inbox renders no emails this time
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 0)
