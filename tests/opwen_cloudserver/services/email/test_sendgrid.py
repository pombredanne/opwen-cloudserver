from unittest import skipUnless

from config import Config
from opwen_cloudserver.services.email.sendgrid import SendGridEmailSender
from tests.opwen_cloudserver.services.email.test_interfaces import Base


@skipUnless(Config.RUN_INTEGRATION_TESTS, 'integration tests disabled')
class TestSendGridEmailSender(Base.TestEmailSender):
    email_sender = SendGridEmailSender(Config.EMAIL_ACCOUNT_KEY)
