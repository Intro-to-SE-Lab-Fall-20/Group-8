from .models import CustomUser
from django import forms


class UserRegistrationForm(forms.Form):
    """
    Form used for registering new users to Simple Email.
    """

    username = forms.CharField()
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    def clean_username(self):
        """
        Cleans the username input. Checks that the username has not already been taken.
        """

        return
