from functools import wraps

from flask import abort
from flask import request

from opwen_email_server import app


def admin_required(func):
    if app.config.get('TESTING'):
        return func

    preshared_secret = app.config.get('PRESHARED_SECRET')

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if preshared_secret and request.args.get('secret') == preshared_secret:
            return func(*args, **kwargs)

        abort(403)

    return decorated_view
