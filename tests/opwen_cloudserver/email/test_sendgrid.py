from unittest import TestCase
from unittest import skipUnless

from config import Config
from opwen_cloudserver.email.sendgrid import SendGridEmailSender
from tests.opwen_cloudserver.email.test_interfaces import TestEmailSender


@skipUnless(Config.RUN_INTEGRATION_TESTS, 'integration tests disabled')
class TestSendGridEmailSender(TestEmailSender, TestCase):
    email_sender = SendGridEmailSender(Config.EMAIL_ACCOUNT_KEY)
