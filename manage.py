#!/usr/bin/env python3

from flask_script import Manager

from opwen_email_server import app
from opwen_email_server.management import SyncDaemonCommand

manager = Manager(app)
manager.add_command('sync-daemon', SyncDaemonCommand)

manager.run()
