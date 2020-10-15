"""
Main file containing tests for unit testing and continuous integration.
https://docs.djangoproject.com/en/3.1/topics/testing/tools/
"""

from django.test import TestCase, Client
from django.contrib import auth

from .models import CustomUser, Email, Sender, Recipient


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


class TestInbox(TestCase):
    """
    Tests the main inbox functionality of the website, along with
    other folders like outbox.
    """

    def setUp(self):
        """
        Sets up some prerequisites before each test.
        """

        # create dummy user to login with
        self.credentials = {
            'username': 'test_user',
            'password': 'test_password'
        }
        self.test_user_one = CustomUser.objects.create_user(**self.credentials)

        # create test client and log in the user
        self.client = Client()
        self.client.login(**self.credentials)

        # create a secondary test user
        self.test_user_two = CustomUser.objects.create_user(
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

    def test_load_outbox(self):
        """
        Tests that the outbox view page loads.
        """

        response = self.client.get('/outbox')

        self.assertEqual(response.status_code, 200)

    def test_inbox_received_emails(self):
        """
        Tests that the inbox view correctly displays emails received by a user.
        """

        # create some test emails that should show up
        create_email(
            subject='Testing subject',
            content='Testing content',
            sender=self.test_user_two,
            recipients=[self.test_user_one],
            is_draft=False,
            is_forward=False
        )
        create_email(
            subject='Another subject',
            content='Even more content',
            sender=self.test_user_two,
            recipients=[self.test_user_one],
            is_draft=False,
            is_forward=False
        )

        # create an email that should NOT show up
        create_email(
            subject='Another subject',
            content='Even more content',
            sender=self.test_user_two,
            recipients=[self.test_user_one],
            is_draft=True,
            is_forward=False
        )

        # check that the inbox renders this email correctly
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 2)

    def test_outbox_sent_emails(self):
        """
        Tests that the inbox view correctly displays emails received by a user.
        """

        # create some test emails that should show up
        create_email(
            subject='Testing subject',
            content='Testing content',
            sender=self.test_user_one,
            recipients=[self.test_user_two],
            is_draft=False,
            is_forward=False
        )
        create_email(
            subject='Another subject',
            content='Even more content',
            sender=self.test_user_one,
            recipients=[self.test_user_two],
            is_draft=False,
            is_forward=False
        )

        # create a test email that should NOT show up
        create_email(
            subject='An invisible subject',
            content='blah blah',
            sender=self.test_user_one,
            recipients=[self.test_user_two],
            is_draft=True,
            is_forward=False
        )

        # check that the inbox renders this email correctly
        response = self.client.get('/outbox')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 2)


class TestSearch(TestCase):
    """
    Tests the website's search functionality.
    """

    def setUp(self):
        """
        Sets up some test users and emails for querying later.
        """

        # create dummy user to login with
        self.credentials = {
            'username': 'user_one',
            'password': 'user_one'
        }
        self.test_user_one = CustomUser.objects.create_user(
            **self.credentials,
            email="user_one@email.com"
        )

        # create test client and log in the user
        self.client = Client()
        self.client.login(**self.credentials)

        # create some additional test users
        self.test_user_two = CustomUser.objects.create_user(
            username="user_two",
            password="user_two",
            email="user_two@email.com"
        )
        self.test_user_three = CustomUser.objects.create_user(
            username="user_three",
            password="user_three",
            email="user_three@email.com"
        )

        # create a test email sent by user one to user two
        self.email_one, self.sender_one, self.recipient_one = create_email(
            subject='subject email sent by user one to user two',
            content='content of email one with something in the body',
            sender=self.test_user_one,
            recipients=[self.test_user_two],
            is_draft=False,
            is_forward=False
        )

        # create a test email sent by user two to user one
        self.email_two, self.sender_two, self.recipient_two = create_email(
            subject='subject email sent by user two to user one',
            content='content of email one with weird in the body',
            sender=self.test_user_two,
            recipients=[self.test_user_one],
            is_draft=False,
            is_forward=False
        )

        # create a test email sent by user one to user three
        self.email_three, self.sender_three, self.recipient_three = create_email(
            subject='subject email sent by user one to user three',
            content='content of email three with a ridiculous word in it',
            sender=self.test_user_one,
            recipients=[self.test_user_three],
            is_draft=False,
            is_forward=False
        )

        # create a test email sent by user two to user three
        self.email_four, self.sender_four, self.recipient_four = create_email(
            subject='subject email from user two to user three',
            content='content of email four with an absolutely spectacular phrase in it',
            sender=self.test_user_two,
            recipients=[self.test_user_three],
            is_draft=False,
            is_forward=False
        )

    def test_empty_results(self):
        """
        Tests if the search view correctly renders empty.
        """

        # submit query
        response = self.client.get(
            '/search/',
            {'query': 'something ridiculously specific that could never exist'},
            follow=True
        )

        # check results
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 0)

    def test_search_by_subject(self):
        """
        Tests searching a user's emails by email subject.
        """

        # submit a specific query
        response = self.client.get('/search/', {'query': self.email_one.subject})

        # check that specific email was returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 1)
        self.assertIsNotNone(response.context['emails'].get(self.email_one.uid))

        # submit a more vague query
        response = self.client.get('/search/', {'query': 'subject'})

        # check that all matching results were returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 3)

    def test_search_by_user(self):
        """
        Tests searching for emails by a user's email.
        """

        # submit query with own email
        response = self.client.get('/search/', {'query': self.test_user_one.email})

        # check results; should return everything sent AND received by user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 3)

        # submit query with another user's email
        response = self.client.get('/search/', {'query': self.test_user_three.email})

        # check results; should only return emails received by said user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 1)
        self.assertIsNotNone(response.context['emails'].get(self.email_three.uid))

        # submit query with recipient user
        response = self.client.get('/search/', {'query': self.test_user_two.email})

        # check results; should only return two emails
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 2)

    def test_search_by_body(self):
        """
        Tests searching for emails by body contents.
        """

        # submit a specific query
        response = self.client.get('/search/', {'query': self.email_two.body})

        # check results
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 1)
        self.assertIsNotNone(response.context['emails'].get(self.email_two.uid))

        # submit a more vague query
        response = self.client.get('/search/', {'query': 'content'})

        # check that all matching results were returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['emails']), 3)

    def test_results_format(self):
        """
        Tests that the search results return in the expected format.
        """

        # submit query with recipient user
        response = self.client.get('/search/', {'query': 'two'})

        # check that there are no duplicates
        self.assertEqual(len(response.context['emails']), 2)

        # check that a received email is formatted correctly
        email_two = response.context['emails'].get(self.email_two.uid)
        self.assertEqual(email_two['from'], self.test_user_two.email)
        self.assertEqual(email_two['to'], self.test_user_one.email)

        # check that a sent email is formatted correctly
        email_one = response.context['emails'].get(self.email_one.uid)
        self.assertEqual(email_one['from'], self.test_user_one.email)
        self.assertEqual(email_one['to'], self.test_user_two.email)
