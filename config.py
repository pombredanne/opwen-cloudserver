from os import getenv
from os import path


app_basedir = path.abspath(path.dirname(__file__))
state_basedir = path.abspath(getenv('OPWEN_STATE_DIRECTORY', app_basedir))


class Config(object):
    EMAIL_ACCOUNT_KEY = getenv('OPWEN_EMAIL_ACCOUNT_KEY')
    EMAIL_HOST = 'ascoderu.ca'

    RUN_INTEGRATION_TESTS = False

    STORAGE_ACCOUNT_KEY = getenv('OPWEN_STORAGE_ACCOUNT_KEY')
    STORAGE_ACCOUNT_NAME = getenv('OPWEN_STORAGE_ACCOUNT_NAME')
    STORAGE_ACCOUNT_CONTAINER = 'opwen'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(state_basedir, 'opwen.db')
    SQLALCHEMY_MIGRATE_REPO = path.join(app_basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
