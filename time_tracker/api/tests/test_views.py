from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


class TestCreateUserView(TestCase):
    """Test the create user view. """

    def setUp(self):
        self.client = APIClient()
        self.create_user_url = reverse('api:create_user')

    def test_create_user_success(self):
        """Test create a valid user is successful. """
        payload = {'username': 'uname', 'email': 'uemail@gmail.com', 'password': 'upass123'}
        res = self.client.post(self.create_user_url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(**res.data).exists())

    def test_username_uniqueness(self):
        """Test that create user fails when username collide with an existing one. """

        payload = {'username': 'uname', 'email': 'uemail@gmail.com', 'password': 'upass123'}
        get_user_model().objects.create_user(**payload)
        res = self.client.post(self.create_user_url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_uniqueness(self):
        """Test that create user fails when email collide with an existing one. """

        payload = {'username': 'uname', 'email': 'uemail@gmail.com', 'password': 'upass123'}
        get_user_model().objects.create_user(**payload)
        payload['username'] = 'new_uname'
        res = self.client.post(self.create_user_url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestManageUserView(TestCase):
    """Test the manager user view. """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='fx',
            email='fx@gmail.com',
            password='fxpass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.manage_user_url = reverse('api:me')

    def test_authentication_required(self):
        """Test that authentication is required for accessing this endpoint. """
        self.client.force_authenticate(user=None)

        # Get
        res = self.client.get(self.manage_user_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Patch
        patch_payload = {'username': 'patch_username'}
        res = self.client.patch(self.manage_user_url, data=patch_payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Delete
        res = self.client.delete(self.manage_user_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_success(self):
        """Test get user profile is successful. """
        res = self.client.get(self.manage_user_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], self.user.username)
        self.assertEqual(res.data['email'], self.user.email)

    def test_update_user_success(self):
        """Test that user profile can be (partially-)updated. """
        # Patch request (partial update)
        patch_payload = {'username': 'patch_username'}
        res = self.client.patch(self.manage_user_url, data=patch_payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], patch_payload['username'])
        self.assertEqual(res.data['email'], self.user.email)

        # Put request (full update)
        put_payload = {
            'username': 'put_username',
            'email': 'putemail@gmail.com',
            'password': 'putpass123',
        }
        res = self.client.put(self.manage_user_url, data=put_payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in put_payload.items():
            # Password (as a write-only field) is not serialized, see serializers.py
            if k != 'password':
                self.assertEqual(res.data[k], v)

    def test_delete_user_success(self):
        """Test that a user can be deleted. """
        res = self.client.delete(self.manage_user_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(get_user_model().objects.exists())


class TestStageViewSet(TestCase):
    """Test the Stage viewset. """

    # def setUp(self):
    #     self.user = get_user_model().objects.create_user(
    #         username='fx',
    #         email='fx@gmail.com',
    #         password='fxpass123',
    #     )
    #     self.client = APIClient()
    #     self.client.force_authenticate(user=self.user)
    #     self.manage_user_url = reverse('api:me')
    #
    # def test_authentication_required(self):
    #     """Test that authentication is required for accessing this endpoint. """
    #     self.client.force_authenticate(user=None)
    #
    #     # Get
    #     res = self.client.get(self.manage_user_url)
    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     # Patch
    #     patch_payload = {'username': 'patch_username'}
    #     res = self.client.patch(self.manage_user_url, data=patch_payload)
    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #     # Delete
    #     res = self.client.delete(self.manage_user_url)
    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
