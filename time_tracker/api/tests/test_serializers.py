from django.test import TestCase

from ..serializers import UserSerializer


class TestUserSerializer(TestCase):
    """Test the user serializer. """

    def test_password_encrypted(self):
        """Test that the password is saved encrypted when creating/updating user. """
        # Create user
        password = 'upass123'
        serializer = UserSerializer(data={'username': 'uname', 'email': 'uemail@gmail.com', 'password': password})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.check_password(password))

        # Update user
        new_password = 'upass456'
        serializer = UserSerializer(user, data={'password': new_password}, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.check_password(new_password))

    def test_password_validation(self):
        """Test that the user serializer is performing Django's default password validation. """
        serializer = UserSerializer(data={'username': '12345', 'email': 'uemail@gmail.com', 'password': '12345'})

        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

        errors_concatenated = ''.join(serializer.errors['password'])
        self.assertIn('too similar', errors_concatenated)
        self.assertIn('too short', errors_concatenated)
        self.assertIn('too common', errors_concatenated)
        self.assertIn('entirely numeric', errors_concatenated)
