from mimetypes import guess_type
from typing import Callable
from typing import Tuple
from urllib.error import HTTPError
from urllib.error import URLError

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import Personalization

from opwen_email_server.utils.log import LogMixin


class SendgridEmailSender(LogMixin):
    def __init__(self, key: str,
                 on_error: Callable[[int, str], None]=None,
                 client: SendGridAPIClient=None,
                 factory: Callable[..., SendGridAPIClient]=SendGridAPIClient
                 ) -> None:
        self._key = key
        self._on_error = on_error
        self.__client = client
        self._client_factory = factory

    @property
    def _client(self) -> SendGridAPIClient:
        if self.__client is not None:
            return self.__client
        client = self._client_factory(apikey=self._key)
        self.__client = client
        return client

    def send_email(self, email: dict) -> bool:
        email = self._create_email(email)
        status, message = self._send_email(email)
        success = status == 202

        if not success and self._on_error:
            self._on_error(status, message)

        return success

    def _send_email(self, email: Mail) -> Tuple[int, str]:
        self.log_debug('about to send email')
        request = email.get()
        try:
            response = self._client.client.mail.send.post(request_body=request)
        except HTTPError as exception:
            self.log_exception('error sending email')
            status = exception.code
            message = str(exception.read())
        except URLError as exception:
            self.log_exception('error sending email')
            status = None
            message = str(exception.reason)
        else:
            self.log_debug('sent email')
            status = response.status_code
            message = str(response.headers)

        return status, message

    @classmethod
    def _create_email(cls, email: dict) -> Mail:
        personalization = Personalization()

        for to in email.get('to', []):
            personalization.add_to(Email(to))
        for cc in email.get('cc', []):
            personalization.add_cc(Email(cc))
        for bcc in email.get('bcc', []):
            personalization.add_bcc(Email(bcc))

        mail = Mail()
        mail.add_personalization(personalization)
        mail.set_subject(email.get('subject'))
        mail.add_content(Content('text/html', email.get('body')))
        mail.set_from(Email(email.get('from')))

        for attachment in email.get('attachments', []):
            mail.add_attachment(cls._create_attachment(attachment))

        return mail

    @classmethod
    def _create_attachment(cls, attachment: dict) -> Attachment:
        filename = attachment.get('filename')
        content = attachment.get('content')

        mail_attachment = Attachment()
        mail_attachment.set_disposition('attachment')
        mail_attachment.set_filename(filename)
        mail_attachment.set_content_id(filename)
        mail_attachment.set_type(guess_type(filename)[0])
        mail_attachment.set_content(content)

        return mail_attachment
