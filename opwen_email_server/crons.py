from opwen_infrastructure.cron import setup_cronjob
from opwen_infrastructure.logging import log_execution

from opwen_email_server import app
from opwen_email_server.actions import DownloadEmailsFromClients
from opwen_email_server.actions import SendEmailsFromClients
from opwen_email_server.actions import UploadEmailsToClients
from opwen_email_server.config import AppConfig


@log_execution(app.logger)
def setup_client_email_upload_cron():
    upload_hour = str(AppConfig.UPLOAD_EMAILS_TO_CLIENT_HOUR_UTC)
    setup_cronjob(hour_utc=upload_hour,
                  method=client_email_upload,
                  logger=app.logger,
                  description='Upload server emails to client at {} UTC'.format(upload_hour))


@log_execution(app.logger)
def setup_client_email_download_cron():
    download_hour = str(AppConfig.DOWNLOAD_CLIENT_EMAILS_HOUR_UTC)
    setup_cronjob(hour_utc=download_hour,
                  method=client_email_download,
                  logger=app.logger,
                  description='Download client emails to server at {} UTC'.format(download_hour))


@log_execution(app.logger)
def setup_client_email_send_cron():
    send_hour = str(AppConfig.SEND_CLIENT_EMAILS_HOUR_UTC)
    setup_cronjob(hour_utc=send_hour,
                  method=client_email_send,
                  logger=app.logger,
                  description='Send client emails via server at {} UTC'.format(send_hour))


@log_execution(app.logger)
def client_email_upload():
    upload_emails_to_clients = UploadEmailsToClients(
        email_store=app.ioc.received_email_store,
        email_sync=app.ioc.email_sync)

    upload_emails_to_clients()


@log_execution(app.logger)
def client_email_send():
    send_emails_from_clients = SendEmailsFromClients(
        email_sender=app.ioc.email_sender,
        email_store=app.ioc.client_email_store)

    send_emails_from_clients()


@log_execution(app.logger)
def client_email_download():
    download_emails_from_clients = DownloadEmailsFromClients(
        email_sync=app.ioc.email_sync,
        email_store=app.ioc.client_email_store)

    download_emails_from_clients()
