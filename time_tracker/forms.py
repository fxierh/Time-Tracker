from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from classic_tracker.models import User


class RegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    def clean(self):
        # Extra validation ensuring username is unique
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username exists")

        # Extra validation ensuring email is unique
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return self.cleaned_data

    class Meta:
        fields = ('username', 'email', 'password1', 'password2')
        model = User


class UserUpdateForm(ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class PasswordResetFormExtended(PasswordResetForm):

    def clean(self):
        # Extra validation ensuring the user email exists
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('User with this email is not found, please double check the spelling')

        return self.cleaned_data
