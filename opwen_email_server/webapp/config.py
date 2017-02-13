from logging import DEBUG
from os import path
from tempfile import gettempdir

from opwen_domain.config import OpwenConfig
from opwen_infrastructure.env import getenv

state_basedir = path.abspath(getenv('OPWEN_STATE_DIRECTORY', gettempdir()))


class AppConfig(OpwenConfig):
    TESTING = getenv('OPWEN_ENABLE_DEBUG')
    PRESHARED_SECRET = getenv('OPWEN_PRESHARED_SECRET')

    CLIENT_EMAIL_STORAGE_ACCOUNT_NAME = getenv('OPWEN_SERVER_ACCOUNT_NAME')
    CLIENT_EMAIL_STORAGE_ACCOUNT_KEY = getenv('OPWEN_SERVER_ACCOUNT_KEY')
    CLIENT_EMAIL_STORAGE_ACCOUNT_CONTAINER = 'client-emails'

    RECEIVED_EMAIL_STORAGE_ACCOUNT_NAME = getenv('OPWEN_SERVER_ACCOUNT_NAME')
    RECEIVED_EMAIL_STORAGE_ACCOUNT_KEY = getenv('OPWEN_SERVER_ACCOUNT_KEY')
    RECEIVED_EMAIL_STORAGE_ACCOUNT_CONTAINER = 'received-emails'

    SENDGRID_ACCOUNT_KEY = getenv('OPWEN_EMAIL_ACCOUNT_KEY')

    LOG_FILE = path.join(state_basedir, 'app.log')
    LOG_FORMAT = '%(asctime)s\t%(levelname)s\t%(message)s'
    LOG_LEVEL = DEBUG
