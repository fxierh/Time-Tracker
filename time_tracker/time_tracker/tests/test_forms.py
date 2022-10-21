from django.test import TestCase
from django.contrib.auth import get_user_model
from ..forms import PasswordResetFormExtended


class TestPasswordResetForm(TestCase):
    """Test the PasswordResetFormExtended form. """

    def test_email_existence_validation(self):
        """Test the validation ensuring the existence of the email entered. """

        get_user_model().objects.create_user(
            username='fx',
            email='123@gmail.com',
            password='password123'
        )

        # For should be valid if email exists
        form = PasswordResetFormExtended(
            data={'email': '123@gmail.com'}
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')

        # For should be invalid if email does not exist
        form = PasswordResetFormExtended(
            data={'email': '124@gmail.com'}
        )
        self.assertEqual(
            form.errors['__all__'],
            ['User with this email is not found, please double check the spelling']
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')
