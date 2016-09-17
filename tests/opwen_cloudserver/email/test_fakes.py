from tests.opwen_cloudserver.email.test_interfaces import TestEmailSender
from tests.utils.fakes import FakeEmailSender


class TestFakeEmailSender(TestEmailSender):
    @property
    def email_sender(self):
        return FakeEmailSender()
