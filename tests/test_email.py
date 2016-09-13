from os import remove
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest import skipUnless

from os.path import relpath

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
        self._files_created = set()

    def tearDown(self):
        for path in self._files_created:
            remove(path)

    def _create_text_file(self, content, encoding='utf-8'):
        """
        :type content: str
        :type encoding: str
        :rtype: str

        """
        with NamedTemporaryFile(dir='.', delete=False) as fobj:
            fobj.write(content.encode(encoding))

        path_created = fobj.name
        self._files_created.add(path_created)
        return relpath(path_created)

    def test_send_email(self):
        success = self.sendgrid.send_email({
            'to': [self.recipient1],
            'from': self.sender,
            'subject': self.test_send_email.__name__,
            'body': 'simple email with <b>formatting</b>',
        })

        self.assertTrue(success)

    def test_send_email_with_attachments(self):
        success = self.sendgrid.send_email({
            'to': [self.recipient1],
            'from': self.sender,
            'subject': self.test_send_email_with_attachments.__name__,
            'body': 'simple email with attachments',
            'attachments': [
                {'filename': 'Some file.txt',
                 'relativepath': self._create_text_file('first file')},
                {'filename': 'Another file.txt',
                 'relativepath': self._create_text_file('second file')}]
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
