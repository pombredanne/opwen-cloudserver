from opwen_email_server.ioc import create_app

app = create_app()

from opwen_email_server import views

from opwen_email_server.crons import setup_client_email_download_cron
from opwen_email_server.crons import setup_client_email_send_cron
from opwen_email_server.crons import setup_client_email_upload_cron

setup_client_email_download_cron()
setup_client_email_upload_cron()
setup_client_email_send_cron()
