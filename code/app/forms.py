from .models import CustomUser, Email, Sender, Recipient
from django import forms
from django.core.exceptions import ValidationError


class UserRegistrationForm(forms.ModelForm):
    """
    Form used for registering new users to Simple Email.
    """

    re_password = forms.CharField(max_length=128)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'password',
            're_password'
        ]

    def clean(self):
        cleaned_data = super().clean()

        # validate passwords match
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("re_password")
        if password != re_password:
            raise ValidationError(
                "Passwords do not match."
            )

    def save(self, commit=True):
        user = super().save(commit=False)

        # hash user password
        user.set_password(self.cleaned_data["password"])

        # create email for user
        user.email = f"{self.cleaned_data['username']}@simpleemail.com"

        # save user to DB
        if commit:
            user.save()

        return user


class ComposeForm(forms.Form):
    """
    Form for creating new emails.
    """

    subject = forms.CharField(strip=True, label='Subject:   ')
    sender = forms.CharField(required=True, label='From:')
    recipients = forms.CharField(required=True, label='Recipients:')
    body = forms.CharField(required=True, label='Body:')
    is_draft = forms.BooleanField(required=False, label='Draft:')
    is_forward = forms.BooleanField(required=False, label='Forward:')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # setup some state vars
        self.sender_user = None
        self.recipient_users = []

    def clean(self):
        """
        Cleans the form's input data.
        """

        # call super clean to do basic cleaning
        super().clean()

        # check if the sender is a real user
        email = self.cleaned_data['sender']
        sender_query = CustomUser.objects.filter(email=email)
        if not sender_query:
            raise ValidationError(f"Invalid sender email: \"{email}\"")
        else:
            self.sender_user = sender_query[0]

        # validate recipients emails
        emails = self.cleaned_data['recipients'].split(',')
        for email in emails:
            email = email.strip()
            if not email:
                continue    # skip this email if it's empty
            recipient_query = CustomUser.objects.filter(email=email)
            if not recipient_query:
                raise ValidationError(f"Invalid recipient email: \"{email}\"")
            else:
                self.recipient_users.append(recipient_query[0])

        # everything checks out
        return

    def create_email_and_relations(self):
        """
        This creates new instances of Email, Sender, and Recipient.
        Returns new instance of Email.
        """

        # validate that this form is valid first
        if not self.is_valid():
            return None

        # create email object
        email = Email.objects.create(
            body=self.cleaned_data['body'],
            subject=self.cleaned_data['subject']
        )

        # create sender object
        sender = Sender.objects.create(
            user=self.sender_user,
            email=email,
            is_draft=self.cleaned_data['is_draft'],
            is_forward=self.cleaned_data['is_forward']
        )

        # create recipients objects
        recipients = []
        for recipient_user in self.recipient_users:
            recipients.append(
                Recipient.objects.create(
                    user=recipient_user,
                    email=email,
                    is_sent=not self.cleaned_data['is_draft'],
                    is_forward=self.cleaned_data['is_forward']
                )
            )

        # everything was created successfully
        return email
