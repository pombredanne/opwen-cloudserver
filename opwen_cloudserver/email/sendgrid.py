from base64 import b64encode
from collections import namedtuple
from mimetypes import guess_type

from urllib.error import HTTPError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail

from opwen_cloudserver.email import EmailSender


# noinspection PyClassHasNoInit
class SendGridResponse(namedtuple('Response', 'status message')):
    pass


class SendGridEmailSender(EmailSender):
    def __init__(self, apikey):
        """
        :type apikey: str

        """
        self._sendgrid = SendGridAPIClient(apikey=apikey)

    def send_email(self, email):
        email = self._create_email(email)
        response = self._send_email(email)
        success = self._check_success(response)

        if not success:
            self._handle_error(response)

        return success

    def _send_email(self, email):
        """
        :type email: Mail
        :rtype: SendGridResponse

        """
        request = email.get()
        try:
            client = self._sendgrid.client.mail.send
            response = client.post(request_body=request)
        except HTTPError as exception:
            status = exception.code
            message = exception.read()
        else:
            status = response.status_code
            message = response.headers

        return SendGridResponse(status=status, message=message)

    @classmethod
    def _handle_error(cls, response):
        """
        :type response: SendGridResponse

        """
        # TODO: handle error properly
        print('{}: {}'.format(response.status, response.message))

    @classmethod
    def _check_success(cls, response):
        """
        :type response: SendGridResponse

        """
        return response.status == 202

    @classmethod
    def _create_email(cls, email):
        """
        :type email: dict
        :rtype Mail

        """
        recipients = set(email.get('to'))

        mail = Mail(to_email=Email(recipients.pop()),
                    from_email=Email(email.get('from')),
                    subject=email.get('subject'),
                    content=Content('text/html', email.get('message')))

        for recipient in recipients:
            mail.personalizations[0].add_to(Email(recipient))

        for attached in email.get('attachments', []):
            mail.add_attachment(cls._create_attachment(
                attached.get('filename'),
                attached.get('relativepath')))

        return mail

    @classmethod
    def _create_attachment(cls, filename, filepath):
        """
        :type filename: str
        :type filepath: str
        :rtype: Attachment

        """
        attachment = Attachment()

        attachment.set_disposition('attachment')
        attachment.set_filename(filename)
        attachment.set_content_id(filename)
        attachment.set_type(guess_type(filename)[0])

        with open(filepath, 'rb') as fobj:
            content = b64encode(fobj.read()).decode('utf-8')
            attachment.set_content(content)

        return attachment
