from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from classic_tracker.models import User
from time_tracker import settings


class EmailTest(TestCase):
    """Test all email sends. """

    def test_password_reset_email(self):
        """Test the password reset email. """

        email = '123@gmail.com'
        user = User.objects.create(username='fx', email=email)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)

        context = {
            'email': email,
            'domain': settings.DOMAIN_NAME,
            'uid': uid,
            'token': token,
        }

        mail.send_mail(
            subject='Password Reset',
            message=render_to_string('password_reset_email.txt', context),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        # Ensure that one message has been sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset', 'Wrong subject')
        self.assertEqual(
            mail.outbox[0].body,
            f"""
Hello,

To reset the password for your account, click the link below:

{settings.DOMAIN_NAME}{reverse('password_reset_confirm', kwargs={'uidb64':uid, 'token':token})}

This link can only be used once. If you need to reset your password again, please submit another request.

If you did not make this request, please ignore this email.

Best regards,

""",
            'Wrong message'
        )
        self.assertEqual(mail.outbox[0].from_email, settings.EMAIL_HOST_USER, 'Wrong sender')
        self.assertEqual(mail.outbox[0].to, [email], 'Wrong receiver')
