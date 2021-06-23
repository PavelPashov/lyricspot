"""Util methods for the lyricspot app."""

import time
from functools import wraps
from flask import redirect, session

from .spotify import get_refresh_token


def login_required(f):
    """Require login for a given route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('country') is None:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def refresh_token(f):
    """Try to refresh the token for a given route."""
    @ wraps(f)
    def decorated_function(*args, **kwargs):
        r_token = session.get('r_token')
        token_time = session.get('token_time')
        if token_time:
            if int(token_time) + 3000 < int(time.time()):
                session['token'] = get_refresh_token(r_token)
                session['token_time'] = int(time.time())
            elif int(token_time) + 3600 < int(time.time()):
                session.clear()
                return redirect('/')
        return f(*args, **kwargs)
    return decorated_function
