from flask import Flask
from opwen_domain.config import OpwenConfig
from opwen_domain.email.tinydb import TinyDbEmailStore
from opwen_domain.mailbox.sendgrid import SendGridEmailReceiver
from opwen_domain.mailbox.sendgrid import SendGridEmailSender
from opwen_domain.sync.azure import AzureAuth
from opwen_domain.sync.azure import MultiClientAzureSync
from opwen_infrastructure.serialization.json import JsonSerializer

from opwen_email_server.config import FlaskConfig


class Ioc(object):
    client_email_store = TinyDbEmailStore(
        store_location=FlaskConfig.CLIENT_EMAIL_STORE)

    received_email_store = TinyDbEmailStore(
        store_location=FlaskConfig.RECEIVED_EMAIL_STORE)

    email_receiver = SendGridEmailReceiver()

    email_sender = SendGridEmailSender(
        apikey=FlaskConfig.SENDGRID_ACCOUNT_KEY)

    email_sync = MultiClientAzureSync(
        auth=AzureAuth(
            account=OpwenConfig.STORAGE_ACCOUNT_NAME,
            key=OpwenConfig.STORAGE_ACCOUNT_KEY,
            container=OpwenConfig.STORAGE_CONTAINER),
        email_info=(
            # the two lines below are not a bug: we want to inverse the up/download
            # because all configs are named from the point of view of the clients
            # e.g. if a client uploads to ~foo and downloads from ~bar then the
            # server needs to upload to ~bar and download from ~foo
            OpwenConfig.STORAGE_UPLOAD_FORMAT,
            OpwenConfig.STORAGE_DOWNLOAD_FORMAT,
            OpwenConfig.EMAIL_HOST_FORMAT.format('')),
        serializer=JsonSerializer())


def create_app():
    """
    :rtype: flask.Flask

    """
    app = Flask(__name__)
    app.config.from_object(FlaskConfig)
    app.ioc = Ioc()

    return app
