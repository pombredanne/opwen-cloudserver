from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from collections import namedtuple
from unittest import TestCase
from unittest import skipUnless
from unittest.mock import Mock
import json

from opwen_tests.config import TestConfig

from opwen_email_server.domain.email.mailbox import SendGridEmailReceiver
from opwen_email_server.domain.email.mailbox import SendGridEmailSender
from tests.data import sendgrid_raw_email_with_attachment
from tests.data import sendgrid_raw_email_with_multiple_recipients


class Base(object):
    class TestEmailReceiver(TestCase, metaclass=ABCMeta):
        @abstractmethod
        def create_email_receiver(self):
            """
            :rtype: opwen_domain.mailbox.EmailReceiver

            """
            raise NotImplementedError

        @abstractproperty
        def given_json_for_email_with_multiple_recipients(self):
            """
            :rtype: str

            """
            raise NotImplementedError

        @abstractproperty
        def given_json_for_email_with_attachment(self):
            """
            :rtype: str

            """
            raise NotImplementedError

        def setUp(self):
            self.email_receiver = self.create_email_receiver()

        def test_parses_email_with_multiple_recipients(self):
            request = Mock(form=json.loads(self.given_json_for_email_with_multiple_recipients))

            # noinspection PyTypeChecker
            email = self.email_receiver.parse_email(request)

            self.assertEqual(email.get('to'), ['to1@vancouver.ascoderu.ca', 'to2@vancouver.ascoderu.ca'])
            self.assertEqual(email.get('cc'), ['cc1@vancouver.ascoderu.ca', 'cc2@vancouver.ascoderu.ca'])
            # TODO: the posted data doesn't contain bcc1, may be a bug in the sendgrid api, https://github.com/sendgrid/sendgrid-python/issues/239
            # self.assertEqual(email.get('bcc'), ['bcc1@vancouver.ascoderu.ca', 'bcc2@vancouver.ascoderu.ca'])
            self.assertEqual(email.get('subject'), 'The subject')
            self.assertEqual(email.get('body'), '<div dir="ltr">The plaintext body.</div>\n')
            self.assertEqual(email.get('sent_at'), '2016-10-29 02:24')

        def test_parses_email_with_attachment(self):
            request = Mock(form=json.loads(self.given_json_for_email_with_attachment))

            # noinspection PyTypeChecker
            email = self.email_receiver.parse_email(request)

            self.assertEqual(email.get('to'), ['to@vancouver.ascoderu.ca'])
            self.assertEqual(email.get('cc'), ['cc@vancouver.ascoderu.ca'])
            self.assertEqual(email.get('bcc'), ['bcc@vancouver.ascoderu.ca'])
            self.assertEqual(email.get('subject'), 'This is the subject')
            self.assertEqual(email.get('body'), '<div dir="ltr">The body goes <b><i><u>here</u></i></b>.</div>\n')
            self.assertEqual(email.get('sent_at'), '2016-10-23 02:42')
            self.assertEqual(len(email.get('attachments', [])), 1)

    class TestEmailSender(TestCase, metaclass=ABCMeta):
        email_domain = 'IntegrationTests.ascoderu.ca'
        recipient1 = 'clemens.wolff+sendgridtest@gmail.com'
        recipient2 = 'clemens.wolff+sendgridtest2@gmail.com'

        @abstractmethod
        def create_email_sender(self):
            """
            :rtype: opwen_domain.mailbox.EmailSender

            """
            raise NotImplementedError

        @property
        def sender(self):
            """
            :rtype: str

            """
            return '{}@{}'.format(self.__class__.__name__, self.email_domain)

        def setUp(self):
            self.email_sender = self.create_email_sender()

        def test_send_email(self):
            success = self.email_sender.send_email({
                'to': [self.recipient1],
                'from': self.sender,
                'subject': self.test_send_email.__name__,
                'message': 'simple email with <b>formatting</b>'})

            self.assertTrue(success)

        def test_send_email_with_attachments(self):
            success = self.email_sender.send_email({
                'to': [self.recipient1],
                'from': self.sender,
                'subject': self.test_send_email_with_attachments.__name__,
                'message': 'simple email with attachments',
                'attachments': [
                    {'filename': 'Some file.txt',
                     'content': b'first file'},
                    {'filename': 'Another file.txt',
                     'content': b'second file'}]})

            self.assertTrue(success)

        def test_send_email_to_multiple_recipients(self):
            success = self.email_sender.send_email({
                'to': [self.recipient1, self.recipient2],
                'from': self.sender,
                'subject': self.test_send_email_to_multiple_recipients.__name__,
                'message': 'simple email with two recipients'})

            self.assertTrue(success)


class SendGridEmailReceiverTests(Base.TestEmailReceiver):
    given_json_for_email_with_multiple_recipients = sendgrid_raw_email_with_multiple_recipients
    given_json_for_email_with_attachment = sendgrid_raw_email_with_attachment

    def create_email_receiver(self):
        return SendGridEmailReceiver()


@skipUnless(reason='integration tests disabled',
            condition=all((TestConfig.RUN_INTEGRATION_TESTS,
                           TestConfig.SENDGRID_API_KEY)))
class SendGridEmailSenderIntegrationTests(Base.TestEmailSender):
    def create_email_sender(self):
        return SendGridEmailSender(apikey=TestConfig.SENDGRID_API_KEY)


class SendGridEmailSenderTests(Base.TestEmailSender):
    def create_email_sender(self):
        return SendGridEmailSender(apikey='fake')

    @classmethod
    def _create_mock_client(cls, status_code=202, headers=''):
        """
        :type status_code: int
        :type headers: str
        :rtype: unittest.mock.Mock

        """
        mock_client = Mock()
        mock_client.post.return_value = FakeResponse(status_code=status_code, headers=headers)
        return mock_client

    def setUp(self):
        super().setUp()
        self.mock_client = self._create_mock_client()
        self.email_sender._create_client = lambda: self.mock_client


# noinspection PyClassHasNoInit
class FakeResponse(namedtuple('Response', 'status_code headers')):
    pass
