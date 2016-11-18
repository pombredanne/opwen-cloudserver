from flask import request
from opwen_infrastructure.flask import debug_route
from opwen_infrastructure.logging import log_execution

from opwen_email_server import app
from opwen_email_server.actions import ReceiveEmail
from opwen_email_server.crons import client_email_download
from opwen_email_server.crons import client_email_send
from opwen_email_server.crons import client_email_upload


@app.route('/inbox', methods=['POST'])
def inbox():
    receive_email = log_execution(app.logger)(ReceiveEmail(
        email_receiver=app.ioc.email_receiver,
        email_store=app.ioc.received_email_store))

    receive_email(request)

    return 'OK'


@debug_route(app, '/download')
def download():
    client_email_download()

    return 'OK'


@debug_route(app, '/send')
def send():
    client_email_send()

    return 'OK'


@debug_route(app, '/upload')
def upload():
    client_email_upload()

    return 'OK'


@app.errorhandler(404)
def _on_404(code_or_exception):
    app.logger.error(code_or_exception)
    return code_or_exception


@app.errorhandler(Exception)
def _on_exception(code_or_exception):
    app.logger.error('%s: %s', code_or_exception.__class__.__name__, code_or_exception)
    return code_or_exception


@app.errorhandler(500)
def _on_500(code_or_exception):
    app.logger.error(code_or_exception)
    return code_or_exception
