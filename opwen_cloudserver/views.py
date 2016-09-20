from flask import request

from opwen_cloudserver import app


@app.route('/inbox', methods=['POST'])
def inbox():
    email = app.email_receiver.parse_email(request)
    app.received_emails_store.add(email)
    return "OK"
