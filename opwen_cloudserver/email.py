from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail


class SendGrid(object):
    def __init__(self, apikey):
        """
        :type apikey: str

        """
        self._sendgrid = SendGridAPIClient(apikey=apikey)

    def send_email(self, email):
        """
        :type email: dict

        """
        email = self._create_email(email)
        response = self._send_email(email)
        success = self._check_success(response)

        if not success:
            self._handle_error(response)

        return success

    def _send_email(self, email):
        """
        :type email: Mail
        :rtype: requests.Response

        """
        return self._sendgrid.client.mail.send.post(request_body=email.get())

    @classmethod
    def _handle_error(cls, response):
        """
        :type response: requests.Response

        """
        # TODO: handle error properly
        print('{}: {}'.format(response.status_code, response.headers))

    @classmethod
    def _check_success(cls, response):
        """
        :type response: requests.Response

        """
        return response.status_code == 202

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
                    content=Content('text/html', email.get('body')))

        for recipient in recipients:
            mail.personalizations[0].add_to(Email(recipient))

        return mail
