"""Setup for E2E tests."""
import os
import time
from src.spotify import get_refresh_token
from src.application import app

app = app

refresh_token = os.environ.get('REFRESH_TOKEN')

token = get_refresh_token(refresh_token)


def set_up_session(client):
    with client.session_transaction() as session:
        session['token'] = token
        session['country'] = 'BG'
        session['token_time'] = time.time()
        session['progress'] = 123
        session['uri'] = 'test'
