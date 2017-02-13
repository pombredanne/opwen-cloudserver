from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple
from datetime import datetime
from functools import partial
from mimetypes import guess_type
from urllib.error import HTTPError
from urllib.error import URLError
import json

from pytz import utc
from sendgrid import SendGridAPIClient
from sendgrid.helpers.inbound import Parse
from sendgrid.helpers.mail import Attachment
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import Personalization


_EMAIL_BODY_CONTENT_TYPES = (
    'text/html',
    'text/plain',
)

_KEYS_TO_PARSE = (
    'from',
    'attachments',
    'headers',
    'text',
    'envelope',
    'to',
    'cc',
    'html',
    'sender_ip',
    'attachment-info',
    'subject',
    'dkim',
    'SPF',
    'charsets',
    'content-ids',
    'spam_report',
    'spam_score',
    'email',
)


class EmailSender(metaclass=ABCMeta):
    @abstractmethod
    def send_email(self, email):
        """
        :type email: dict
        :rtype bool

        """
        raise NotImplementedError


class EmailReceiver(metaclass=ABCMeta):
    @abstractmethod
    def parse_email(self, request):
        """
        :type request: flask.Request
        :rtype: dict

        """
        raise NotImplementedError


# noinspection PyClassHasNoInit
class _SendGridResponse(namedtuple('Response', 'status message')):
    pass


# noinspection PyClassHasNoInit
class _SendGridParseConfig(namedtuple('Config', 'keys')):
    pass


def _parse_and_set_envelope_value(parsed, email, email_key, envelope_key=None):
    """
    :type parsed: dict
    :type email: dict
    :type email_key: str
    :type envelope_key: str

    """
    value = parsed.get('envelope', {}).get(envelope_key or email_key)
    if value:
        email.setdefault(email_key, value)


def _parse_and_set_value(parsed, email, email_key, parsed_key=None, default_factory=None):
    """
    :type parsed: dict
    :type email: dict
    :type email_key: str
    :type parsed_key: str
    :type default_factory: X -> Y

    """
    field_value = parsed.get(parsed_key or email_key)
    if field_value:
        if default_factory:
            field_value = default_factory(field_value)
        email.setdefault(email_key, field_value)


def _parse_attachments(attachments):
    """
    :type attachments: collections.Iterable[dict]
    :rtype: collections.Iterable[dict]

    """
    for attachment in attachments:
        content_type = attachment.get('type')
        if content_type not in _EMAIL_BODY_CONTENT_TYPES:
            filename = attachment.get('file_name')
            content = attachment.get('contents')
            if filename and content:
                yield {'filename': filename,
                       'content': content}


def _parse_and_set_attachments(attachments, email):
    """
    :type attachments: list[dict] | None
    :type email: dict

    """
    if not attachments:
        return

    email['attachments'] = list(_parse_attachments(attachments))


def _get_encoding(message, fallback='ascii'):
    """
    :type message: email.message.Message
    :type fallback: str
    :rtype: str

    """
    return message.get_content_charset() or message.get_charset() or fallback


def _get_payload(message):
    """
    :type message: email.message.Message
    :rtype: str

    """
    encoded = message.get_payload(decode=True)
    decoded = encoded.decode(_get_encoding(message), errors='replace')
    return decoded


def _parse_body(message, content_type):
    """
    :type message: email.message.Message
    :rtype: str

    """
    if message.is_multipart():
        parts = message.get_payload()
        bodies = (_parse_body(part, content_type) for part in parts)
        return '\n\n'.join(filter(None, bodies))

    if message.get_content_type() == content_type:
        return _get_payload(message)

    return None


def _parse_and_set_body(parsed, email):
    """
    :type parsed: email.message.Message
    :type email: dict

    """
    for content_type in _EMAIL_BODY_CONTENT_TYPES:
        content = _parse_body(parsed, content_type)
        if content:
            email.setdefault('body', content)
            break


def _parse_and_set_sent_at(parsed, email):
    """
    :type parsed: email.message.Message
    :type email: dict

    """
    sent_at = parsed.get('Date')
    if not sent_at:
        return

    try:
        sent_at = datetime.strptime(sent_at, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        # todo: add logging
        return

    sent_at = sent_at.astimezone(utc)
    sent_at = sent_at.strftime('%Y-%m-%d %H:%M')
    email['sent_at'] = sent_at


def _split_addresses(addresses):
    """
    :type addresses: str
    :rtype: list[str]

    """
    return addresses.split(', ')


_parse_and_set_from = partial(_parse_and_set_envelope_value, email_key='from')
_parse_and_set_bcc = partial(_parse_and_set_envelope_value, email_key='bcc', envelope_key='to')
_parse_and_set_to = partial(_parse_and_set_value, email_key='to', default_factory=_split_addresses)
_parse_and_set_cc = partial(_parse_and_set_value, email_key='cc', default_factory=_split_addresses)
_parse_and_set_subject = partial(_parse_and_set_value, email_key='subject')


class SendGridEmailReceiver(EmailReceiver):
    def __init__(self):
        self._config = _SendGridParseConfig(keys=_KEYS_TO_PARSE)

    def parse_email(self, request):
        parsed, metadata, attachments = self._parse(request)
        email = {}
        _parse_and_set_attachments(attachments, email)
        _parse_and_set_to(metadata, email)
        _parse_and_set_cc(metadata, email)
        _parse_and_set_bcc(metadata, email)
        _parse_and_set_from(metadata, email)
        _parse_and_set_subject(metadata, email)
        _parse_and_set_body(parsed, email)
        _parse_and_set_sent_at(parsed, email)
        return email

    def _parse(self, request):
        """
        :type request: flask.Request
        :rtype: (email.message.Message, dict, list[dict])

        """
        parsed = Parse(self._config, request)
        metadata = parsed.key_values()
        metadata['envelope'] = json.loads(metadata.get('envelope', '{}'))
        attachments = parsed.attachments()
        email = parsed.get_raw_email()
        return email, metadata, attachments


class SendGridEmailSender(EmailSender):
    def __init__(self, apikey):
        """
        :type apikey: str

        """
        self._apikey = apikey

    def _create_client(self):
        return SendGridAPIClient(apikey=self._apikey).client.mail.send

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
        :rtype: _SendGridResponse

        """
        client = self._create_client()
        request = email.get()
        try:
            response = client.post(request_body=request)
        except HTTPError as exception:
            status = exception.code
            message = exception.read()
        except URLError as exception:
            status = None
            message = exception.reason
        else:
            status = response.status_code
            message = response.headers

        return _SendGridResponse(status=status, message=message)

    # noinspection PyMethodMayBeStatic
    def _handle_error(self, response):
        """
        :type response: _SendGridResponse

        """
        pass

    @classmethod
    def _check_success(cls, response):
        """
        :type response: _SendGridResponse

        """
        return response.status == 202

    @classmethod
    def _create_email(cls, email):
        """
        :type email: dict
        :rtype Mail

        """
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
    def _create_attachment(cls, attachment):
        """
        :type attachment: dict
        :rtype: Attachment

        """
        filename = attachment.get('filename')
        content = attachment.get('content')

        attachment = Attachment()
        attachment.set_disposition('attachment')
        attachment.set_filename(filename)
        attachment.set_content_id(filename)
        attachment.set_type(guess_type(filename)[0])
        attachment.set_content(content)

        return attachment
