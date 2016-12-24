from logging import DEBUG
from os import path
from tempfile import gettempdir

from opwen_domain.config import OpwenConfig
from opwen_infrastructure.env import getenv

state_basedir = path.abspath(getenv('OPWEN_STATE_DIRECTORY', gettempdir()))


class AppConfig(OpwenConfig):
    SECRET_KEY = getenv('OPWEN_SECRET_KEY')
    SECURITY_PASSWORD_SALT = getenv('OPWEN_PASSWORD_SALT')

    TESTING = getenv('OPWEN_ENABLE_DEBUG')

    CLIENT_EMAIL_STORE = path.join(state_basedir, 'client-email.store')

    CLIENT_EMAIL_STORAGE_ACCOUNT_NAME = getenv('OPWEN_SERVER_ACCOUNT_NAME')
    CLIENT_EMAIL_STORAGE_ACCOUNT_KEY = getenv('OPWEN_SERVER_ACCOUNT_KEY')
    CLIENT_EMAIL_STORAGE_ACCOUNT_CONTAINER = 'client-emails'

    RECEIVED_EMAIL_STORAGE_ACCOUNT_NAME = getenv('OPWEN_SERVER_ACCOUNT_NAME')
    RECEIVED_EMAIL_STORAGE_ACCOUNT_KEY = getenv('OPWEN_SERVER_ACCOUNT_KEY')
    RECEIVED_EMAIL_STORAGE_ACCOUNT_CONTAINER = 'received-emails'

    SENDGRID_ACCOUNT_KEY = getenv('OPWEN_EMAIL_ACCOUNT_KEY')

    UPLOAD_EMAILS_TO_CLIENT_HOUR_UTC = (OpwenConfig.EMAIL_SYNC_HOUR_UTC - 1) % 24
    DOWNLOAD_CLIENT_EMAILS_HOUR_UTC = (OpwenConfig.EMAIL_SYNC_HOUR_UTC + 1) % 24
    SEND_CLIENT_EMAILS_HOUR_UTC = (DOWNLOAD_CLIENT_EMAILS_HOUR_UTC + 1) % 24

    DAEMON_LOG_FILE = path.join(state_basedir, 'daemon.log')
    APP_LOG_FILE = path.join(state_basedir, 'app.log')
    LOG_FORMAT = '%(asctime)s\t%(levelname)s\t%(pathname)s:%(lineno)d\t%(message)s'
    LOG_LEVEL = DEBUG
