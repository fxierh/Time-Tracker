from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestUserAdmin(TestCase):
    """Test admin pages related to the user model."""

    def setUp(self):
        self.client = Client()
        # create_superuser and create_user hashes password, but create does not
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='admin_password'
        )
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='user',
            password='user_password',
        )
        self.client.force_login(self.admin_user)

    def test_list_user_page(self):
        """Test that users are listed on user page"""

        url = reverse('admin:classic_tracker_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.email)

    def test_change_user_page(self):
        """Test that the user change page works"""

        url = reverse('admin:classic_tracker_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""

        url = reverse('admin:classic_tracker_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
