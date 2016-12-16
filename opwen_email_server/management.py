from logging import getLogger

from flask_script import Command

from opwen_email_server.actions import DownloadEmailsFromClients
from opwen_email_server.actions import UploadEmailsToClients
from opwen_email_server.actions import SendEmailsFromClients
from opwen_email_server.config import AppConfig
from opwen_email_server.ioc import Ioc
from opwen_infrastructure.cron import CronCommand
from opwen_infrastructure.cron import CronCommandMixin


class SyncDaemonCommand(CronCommandMixin, Command):
    def __init__(self):
        logger = getLogger()
        logger.setLevel(AppConfig.LOG_LEVEL)

        CronCommandMixin.__init__(
            self,
            logger,
            CronCommand(
                description='upload emails from server to clients',
                scheduled_hour_utc=str(AppConfig.UPLOAD_EMAILS_TO_CLIENT_HOUR_UTC),
                command=UploadEmailsToClients(
                    email_store=Ioc.received_email_store,
                    email_sync=Ioc.email_sync)),
            CronCommand(
                description='download emails from clients to server',
                scheduled_hour_utc=str(AppConfig.DOWNLOAD_CLIENT_EMAILS_HOUR_UTC),
                command=DownloadEmailsFromClients(
                    email_sync=Ioc.email_sync,
                    email_store=Ioc.client_email_store)),
            CronCommand(
                description='send emails from clients',
                scheduled_hour_utc=str(AppConfig.SEND_CLIENT_EMAILS_HOUR_UTC),
                command=SendEmailsFromClients(
                    email_sender=Ioc.email_sender,
                    email_store=Ioc.client_email_store)))
