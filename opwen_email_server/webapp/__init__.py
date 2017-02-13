# pylint: disable=wrong-import-position
from opwen_email_server.webapp.ioc import create_app

app = create_app()

from opwen_email_server.webapp import login
from opwen_email_server.webapp import views
