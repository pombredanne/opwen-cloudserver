from unittest import TestCase
from unittest import skipUnless

from config import Config
from opwen_cloudserver.email import SendGrid


@skipUnless(Config.RUN_INTEGRATION_TESTS, 'integration tests disabled')
class TestSendGrid(TestCase):
    recipient1 = 'clemens.wolff+sendgridtest@gmail.com'
    recipient2 = 'clemens.wolff+sendgridtest2@gmail.com'

    @property
    def sender(self):
        return '{}@{}'.format(self.__class__.__name__, Config.EMAIL_HOST)

    def setUp(self):
        self.sendgrid = SendGrid(Config.EMAIL_ACCOUNT_KEY)

    def test_send_email(self):
        success = self.sendgrid.send_email({
            'to': [self.recipient1],
            'from': self.sender,
            'subject': self.test_send_email.__name__,
            'body': 'simple email with <b>formatting</b>',
        })

        self.assertTrue(success)

    def test_send_email_to_multiple_recipients(self):
        success = self.sendgrid.send_email({
            'to': [self.recipient1, self.recipient2],
            'from': self.sender,
            'subject': self.test_send_email_to_multiple_recipients.__name__,
            'body': 'simple email with two recipients',
        })

        self.assertTrue(success)
