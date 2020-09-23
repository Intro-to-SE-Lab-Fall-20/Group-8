from .models import CustomUser
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
    Form for creating new emails. This creates new instances of Email, Sender, and Recipient.
    """

    subject = forms.CharField(strip=True)
    sender = forms.CharField(required=True)
    recipients = forms.CharField(required=True)
    body = forms.CharField(required=True)
    is_draft = forms.BooleanField(initial=False)

    def clean(self):
        # check if the sender is a real user
        email = self.cleaned_data['sender']
        username = email.split('@')[0]
        sender_query = CustomUser.objects.filter(username=username)
        if not sender_query:
            raise ValidationError(f"Invalid sender email: \"{email}\"")

        # validate recipients emails
        emails = self.cleaned_data['recipients'].split(',')
        for email in emails:
            username = email.split('@')[0]
            recipient_query = CustomUser.objects.filter(username=username)
            print(sender_query, username)
            if not recipient_query:
                raise ValidationError(f"Invalid recipient email: \"{email}\"")

        # everything checks out
        return
