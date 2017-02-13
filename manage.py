#!/usr/bin/env python3

from flask_script import Manager

from opwen_email_server.webapp import app

manager = Manager(app)

manager.run()
