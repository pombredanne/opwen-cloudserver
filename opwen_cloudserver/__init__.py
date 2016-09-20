from flask import Flask

from config import Config
from opwen_cloudserver.services.email.sendgrid import SendGridEmailReceiver
from tests.utils.fakes import FakeReceivedEmailsStore

app = Flask(__name__)

app.email_receiver = SendGridEmailReceiver(Config.SENDGRID_KEYS_TO_PARSE)
app.received_emails_store = FakeReceivedEmailsStore(Config.EMAIL_HOST)

from opwen_cloudserver import views
