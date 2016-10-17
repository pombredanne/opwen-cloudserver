from os import getenv
from os import path
from tempfile import gettempdir

from opwen_domain.config import OpwenConfig

state_basedir = path.abspath(getenv('OPWEN_STATE_DIRECTORY', gettempdir()))


class FlaskConfig(object):
    SECRET_KEY = getenv('OPWEN_SECRET_KEY')
    SECURITY_PASSWORD_SALT = getenv('OPWEN_PASSWORD_SALT')

    TESTING = getenv('OPWEN_ENABLE_DEBUG', False)

    CLIENT_EMAIL_STORE = path.join(state_basedir, 'client-email.store')
    RECEIVED_EMAIL_STORE = path.join(state_basedir, 'received-email.store')

    SENDGRID_ACCOUNT_KEY = getenv('OPWEN_EMAIL_ACCOUNT_KEY')
    SENDGRID_KEYS_TO_PARSE = (
        'from',
        'attachments',
        'headers',
        'text',
        'envelope',
        'to',
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

    UPLOAD_EMAILS_TO_CLIENT_HOUR_UTC = (OpwenConfig.EMAIL_SYNC_HOUR_UTC - 1) % 24
    DOWNLOAD_CLIENT_EMAILS_HOUR_UTC = (OpwenConfig.EMAIL_SYNC_HOUR_UTC + 1) % 24
    SEND_CLIENT_EMAILS_HOUR_UTC = (DOWNLOAD_CLIENT_EMAILS_HOUR_UTC + 1) % 24
