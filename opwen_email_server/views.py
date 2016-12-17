from flask import request
from opwen_infrastructure.flask import debug_route
from opwen_infrastructure.logging import log_execution

from opwen_email_server import app
from opwen_email_server.actions import DownloadEmailsFromClients
from opwen_email_server.actions import UploadEmailsToClients
from opwen_email_server.actions import ReceiveEmail
from opwen_email_server.actions import SendEmailsFromClients


@app.route('/inbox', methods=['POST'])
def inbox():
    receive_email = log_execution(app.logger)(ReceiveEmail(
        email_receiver=app.ioc.email_receiver,
        email_store=app.ioc.received_email_store))

    receive_email(request)

    return 'OK'


@debug_route(app, '/download')
def download():
    client_email_download = DownloadEmailsFromClients(
        email_sync=app.ioc.email_sync,
        email_store=app.ioc.client_email_store)

    client_email_download()

    return 'OK'


@debug_route(app, '/send')
def send():
    client_email_send = SendEmailsFromClients(
        email_sender=app.ioc.email_sender,
        email_store=app.ioc.client_email_store)

    client_email_send()

    return 'OK'


@debug_route(app, '/upload')
def upload():
    client_email_upload = UploadEmailsToClients(
        email_store=app.ioc.received_email_store,
        email_sync=app.ioc.email_sync)

    client_email_upload()

    return 'OK'


@app.errorhandler(404)
def _on_404(code_or_exception):
    app.logger.warning('404: %s', request.path)
    return code_or_exception


@app.errorhandler(Exception)
def _on_exception(code_or_exception):
    app.logger.error('%s: %s', code_or_exception.__class__.__name__, code_or_exception)
    return code_or_exception


@app.errorhandler(500)
def _on_500(code_or_exception):
    app.logger.error(code_or_exception)
    return code_or_exception
