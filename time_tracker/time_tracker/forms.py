from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput
from django.utils.translation import gettext_lazy as _

from classic_tracker.models import User


class RegistrationForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=EmailInput(attrs={
            'class': 'form-control',
            'size': 20,
        }),
        help_text="<ul><li>Your email will NOT be shared with anyone.</li><li>ONLY non-promotional emails "
                  "(like for password reset) are sent.</li></ul> "
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'size': 20,
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'size': 20,
        }),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        fields = ('username', 'email', 'password1', 'password2')
        model = User

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'size': 20,
            })
        }


class UserLoginForm(AuthenticationForm):

    username = UsernameField(
        widget=forms.TextInput(attrs={
                'class': 'form-control',
                'size': 20,
        })
    )

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'size': 20,
        })
    )


class UserUpdateForm(ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',  # For Bootstrap
                'size': 20,
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
                'readonly': '',
                'size': 20,
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control',
                'size': 20,
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
                'size': 20,
            }),
        }


class PasswordResetFormExtended(PasswordResetForm):

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'form-control',
            'size': 20,
        }),
    )

    def clean(self):
        # Extra validation ensuring the user email exists
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('User with this email is not found, please double check the spelling')

        return self.cleaned_data
