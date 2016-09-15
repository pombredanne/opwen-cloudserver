from os import getenv


class Config(object):
    EMAIL_ACCOUNT_KEY = getenv('OPWEN_EMAIL_ACCOUNT_KEY')
    EMAIL_HOST = 'ascoderu.ca'

    RUN_INTEGRATION_TESTS = False

    STORAGE_ACCOUNT_KEY = getenv('OPWEN_STORAGE_ACCOUNT_KEY')
    STORAGE_ACCOUNT_NAME = getenv('OPWEN_STORAGE_ACCOUNT_NAME')
    STORAGE_ACCOUNT_CONTAINER = 'opwen'
