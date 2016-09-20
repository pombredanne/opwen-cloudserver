from tests.opwen_cloudserver.services.email.test_interfaces import Base
from tests.utils.fakes import FakeEmailSender


class TestFakeEmailSender(Base.TestEmailSender):
    @property
    def email_sender(self):
        return FakeEmailSender()
