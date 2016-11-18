from flask import request
from opwen_infrastructure.cron import setup_cronjob
from opwen_infrastructure.logging import log_execution
from opwen_infrastructure.flask import debug_route

from opwen_email_server import app
from opwen_email_server.actions import DownloadEmailsFromClients
from opwen_email_server.actions import ReceiveEmail
from opwen_email_server.actions import SendEmailsFromClients
from opwen_email_server.actions import UploadEmailsToClients
from opwen_email_server.config import AppConfig


@app.route('/inbox', methods=['POST'])
def inbox():
    receive_email = log_execution(app.logger)(ReceiveEmail(
        email_receiver=app.ioc.email_receiver,
        email_store=app.ioc.received_email_store))

    receive_email(request)

    return 'OK'


@app.before_first_request
@log_execution(app.logger)
def _setup_upload_emails_to_clients_cron():
    upload_hour = str(AppConfig.UPLOAD_EMAILS_TO_CLIENT_HOUR_UTC)
    setup_cronjob(hour_utc=upload_hour,
                  method=_upload_emails_to_clients,
                  logger=app.logger,
                  description='Upload server emails to client at {} UTC'.format(upload_hour))


@app.before_first_request
@log_execution(app.logger)
def _setup_download_emails_from_clients_cron():
    download_hour = str(AppConfig.DOWNLOAD_CLIENT_EMAILS_HOUR_UTC)
    setup_cronjob(hour_utc=download_hour,
                  method=_download_emails_from_clients,
                  logger=app.logger,
                  description='Download client emails to server at {} UTC'.format(download_hour))


@app.before_first_request
@log_execution(app.logger)
def _setup_send_emails_from_clients_cron():
    send_hour = str(AppConfig.SEND_CLIENT_EMAILS_HOUR_UTC)
    setup_cronjob(hour_utc=send_hour,
                  method=_send_email_from_clients,
                  logger=app.logger,
                  description='Send client emails via server at {} UTC'.format(send_hour))


@debug_route(app, '/upload')
@log_execution(app.logger)
def _upload_emails_to_clients():
    upload_emails_to_clients = UploadEmailsToClients(
        email_store=app.ioc.received_email_store,
        email_sync=app.ioc.email_sync)

    upload_emails_to_clients()

    return 'OK'


@debug_route(app, '/send')
@log_execution(app.logger)
def _send_email_from_clients():
    send_emails_from_clients = SendEmailsFromClients(
        email_sender=app.ioc.email_sender,
        email_store=app.ioc.client_email_store)

    send_emails_from_clients()

    return 'OK'


@debug_route(app, '/download')
@log_execution(app.logger)
def _download_emails_from_clients():
    download_emails_from_clients = DownloadEmailsFromClients(
        email_sync=app.ioc.email_sync,
        email_store=app.ioc.client_email_store)

    download_emails_from_clients()

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
