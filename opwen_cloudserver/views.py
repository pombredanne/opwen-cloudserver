from flask import request

from config import Config
from opwen_cloudserver import app
from opwen_cloudserver.actions import ReceiveEmail
from opwen_cloudserver.services.email.sendgrid import SendGridEmailReceiver
from tests.utils.fakes import FakeReceivedEmailsStore


@app.route('/inbox', methods=['POST'])
def inbox():
    receive_email = ReceiveEmail(
        email_receiver=SendGridEmailReceiver(Config.SENDGRID_KEYS_TO_PARSE),
        received_emails_store=FakeReceivedEmailsStore(Config.EMAIL_HOST))

    success = receive_email(request)

    if success:
        return "OK", 200
    else:
        return "FAIL", 500
