import os

from flask import request
from flask import send_from_directory

from opwen_infrastructure.logging import log_execution

from opwen_email_server.webapp import app
from opwen_email_server.webapp.actions import DownloadEmailsFromClients
from opwen_email_server.webapp.actions import ReceiveEmail
from opwen_email_server.webapp.actions import SendEmailsFromClients
from opwen_email_server.webapp.actions import UploadEmailsToClients
from opwen_email_server.webapp.login import admin_required


@app.route('/inbox', methods=['POST'])
@log_execution(app.logger)
def inbox():
    receive_email = ReceiveEmail(
        email_receiver=app.ioc.email_receiver,
        email_store=app.ioc.received_email_store)

    receive_email(request)

    return 'OK'


@app.route('/download')
@admin_required
@log_execution(app.logger)
def download():
    client_email_download = DownloadEmailsFromClients(
        email_sync=app.ioc.email_sync,
        email_store=app.ioc.client_email_store)

    client_email_download()

    return 'OK'


@app.route('/send')
@admin_required
@log_execution(app.logger)
def send():
    client_email_send = SendEmailsFromClients(
        email_sender=app.ioc.email_sender,
        email_store=app.ioc.client_email_store)

    client_email_send()

    return 'OK'


@app.route('/upload')
@admin_required
@log_execution(app.logger)
def upload():
    client_email_upload = UploadEmailsToClients(
        email_store=app.ioc.received_email_store,
        email_sync=app.ioc.email_sync)

    client_email_upload()

    return 'OK'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static'),
        filename='favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.route('/robots.txt')
def robots():
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static'),
        filename='robots.txt',
        mimetype='text/plain')


@app.errorhandler(404)
def _on_404(code_or_exception):
    app.logger.debug('404: %s', request.path)
    return code_or_exception


@app.errorhandler(Exception)
def _on_exception(code_or_exception):
    app.logger.error('%s: %s', code_or_exception.__class__.__name__, code_or_exception)
    return code_or_exception


@app.errorhandler(500)
def _on_500(code_or_exception):
    app.logger.error(code_or_exception)
    return code_or_exception
