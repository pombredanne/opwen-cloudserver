from json import dumps
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from opwen_domain.email.azure import AzureEmailStore
from opwen_domain.mailbox.sendgrid import SendGridEmailReceiver
from opwen_domain.mailbox.sendgrid import SendGridEmailSender
from opwen_domain.sync.azure import AzureAuth
from opwen_domain.sync.azure import MultiClientAzureSync
from opwen_infrastructure.serialization.json import JsonSerializer

from opwen_email_server.config import AppConfig


class Ioc(object):
    serializer = JsonSerializer()

    client_email_store = AzureEmailStore(
        auth=AzureAuth(
            account=AppConfig.CLIENT_EMAIL_STORAGE_ACCOUNT_NAME,
            key=AppConfig.CLIENT_EMAIL_STORAGE_ACCOUNT_KEY,
            container=AppConfig.CLIENT_EMAIL_STORAGE_ACCOUNT_CONTAINER),
        serializer=serializer)

    received_email_store = AzureEmailStore(
        auth=AzureAuth(
            account=AppConfig.RECEIVED_EMAIL_STORAGE_ACCOUNT_NAME,
            key=AppConfig.RECEIVED_EMAIL_STORAGE_ACCOUNT_KEY,
            container=AppConfig.RECEIVED_EMAIL_STORAGE_ACCOUNT_CONTAINER),
        serializer=serializer)

    email_receiver = SendGridEmailReceiver()

    email_sender = SendGridEmailSender(
        apikey=AppConfig.SENDGRID_ACCOUNT_KEY)

    email_sync = MultiClientAzureSync(
        auth=AzureAuth(
            account=AppConfig.STORAGE_ACCOUNT_NAME,
            key=AppConfig.STORAGE_ACCOUNT_KEY,
            container=AppConfig.STORAGE_CONTAINER),
        email_info=(
            # the two lines below are not a bug: we want to inverse the up/download
            # because all configs are named from the point of view of the clients
            # e.g. if a client uploads to ~foo and downloads from ~bar then the
            # server needs to upload to ~bar and download from ~foo
            AppConfig.STORAGE_UPLOAD_FORMAT,
            AppConfig.STORAGE_DOWNLOAD_FORMAT,
            AppConfig.EMAIL_HOST_FORMAT.format('')),
        serializer=serializer)


def create_app():
    """
    :rtype: flask.Flask

    """
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    app.ioc = Ioc()

    logger = TimedRotatingFileHandler(filename=AppConfig.LOG_FILE,
                                      when='H', interval=1, delay=True,
                                      utc=True, encoding='utf-8')
    logger.setFormatter(Formatter(AppConfig.LOG_FORMAT))
    app.logger.addHandler(logger)
    app.logger.setLevel(AppConfig.LOG_LEVEL)

    app.logger.info('config: {}'.format(dumps(app.config, indent=2, sort_keys=True)))

    return app
