from .models import CustomUser
from django import forms


class UserRegistrationForm(forms.Form):
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
