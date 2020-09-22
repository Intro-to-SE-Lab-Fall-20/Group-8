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
