from flask import Flask
from opwen_domain.config import OpwenConfig
from opwen_domain.email.tinydb import TinyDbEmailStore
from opwen_domain.mailbox.sendgrid import SendGridEmailReceiver
from opwen_domain.mailbox.sendgrid import SendGridEmailSender
from opwen_domain.sync.azure import AzureSync
from opwen_infrastructure.serialization.json import JsonSerializer

from opwen_email_server.config import FlaskConfig


class Ioc(object):
    client_email_store = TinyDbEmailStore(
        store_location=FlaskConfig.CLIENT_EMAIL_STORE)

    received_email_store = TinyDbEmailStore(
        store_location=FlaskConfig.RECEIVED_EMAIL_STORE)

    email_receiver = SendGridEmailReceiver(
        keys_to_parse=FlaskConfig.SENDGRID_KEYS_TO_PARSE)

    email_sender = SendGridEmailSender(
        apikey=FlaskConfig.SENDGRID_ACCOUNT_KEY)

    email_sync = AzureSync(
        account_name=OpwenConfig.STORAGE_ACCOUNT_NAME,
        account_key=OpwenConfig.STORAGE_ACCOUNT_KEY,
        container=OpwenConfig.STORAGE_CONTAINER,
        download_location=OpwenConfig.STORAGE_UPLOAD_PATH,
        upload_location=OpwenConfig.STORAGE_UPLOAD_PATH,
        serializer=JsonSerializer())  # TODO: create multiplexer


def create_app():
    """
    :rtype: flask.Flask

    """
    app = Flask(__name__)
    app.config.from_object(FlaskConfig)
    app.ioc = Ioc()

    return app
