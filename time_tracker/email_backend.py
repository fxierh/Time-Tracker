import boto3

from botocore.exceptions import ClientError

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class AmazonSESEmailBackend(BaseEmailBackend):
    """
    Send email through Amazon SES's API
    """
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)

        # Get configuration from AWS prefixed settings in settings.py
        self.aws_access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID", None)
        self.aws_secret_key = getattr(settings, "AWS_SECRET_KEY", None)
        self.aws_region = getattr(settings, "AWS_REGION", None)

        # AWS connection
        self.client = boto3.client(
            "ses",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region,
        )

        # Other settings
        self.charset = "UTF-8"

    def send_messages(self, email_messages):
        """
        Send one or more messages, each from one sender to one or more recipients.
        :param email_messages: a list of Django EmailMessage Objects
        :return: the number of email messages sent
        """

        sent_message_count = 0
        for email_message in email_messages:
            sent_message_count += self._send(email_message)

        return sent_message_count

    def _send(self, email_message):
        """
        Send individual email to one or more recipients.

        Note:
        The sender address must be verified with Amazon SES.
        If your account is still in the sandbox, the receiver address must be verified as well.
        :param email_message:
        :return: True (success) or False (fail)
        """

        # Try to send the email
        try:
            kwargs = {
                'Source': email_message.from_email,
                'Destination': {'ToAddresses': list(email_message.to)},
                'Message': {
                    'Body': {
                        'Text': {
                            'Charset': self.charset,
                            'Data': email_message.body,
                        },
                    },
                    'Subject': {
                        'Charset': self.charset,
                        'Data': email_message.subject,
                    },
                },
            }

            # If the html_message argument is passed in the send_mail function in views.py
            if email_message.alternatives:
                kwargs['Message']['Body']['Html'] = {
                    'Charset': self.charset,
                    'Data': email_message.alternatives[0][0],
                }

            self.client.send_email(**kwargs)
        except ClientError:
            print(f"Email send from {email_message.from_email} to {email_message.to} Failed")
            return False

        return True
