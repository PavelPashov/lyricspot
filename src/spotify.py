"""Methods for authenticating and using the Spotify API."""

from flask import request, session
from urllib.parse import urlencode

import base64
import json
import logging
import os
import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
FLASK_ENV = os.environ.get("FLASK_ENV")

SCOPE = 'user-read-email user-read-recently-played user-top-read \
        user-read-recently-played user-read-playback-state user-read-currently-playing user-read-private \
        user-modify-playback-state'

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = 'v1'

data_bytes = f'{CLIENT_ID}:{CLIENT_SECRET}'

encoded = base64.urlsafe_b64encode(data_bytes.encode()).decode()

REDIRECT_URI = os.environ.get("REDIRECT_URI")

if FLASK_ENV == 'development':
    REDIRECT_URI = 'http://127.0.0.1:5000/hello'


def generate_authorize_url():
    """Generate the URL which will be used for authentication."""
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
    }

    return f'{SPOTIFY_AUTH_URL}?{urlencode(params)}'


def generate_access_token_url():
    """Generate the url for the access token."""
    auth_token = request.args['code']

    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
    return post_request


def get_refresh_token(r_token):
    """Get the refresh token."""
    url = 'https://accounts.spotify.com/api/token'

    headers = {
        'Authorization': f'Basic {encoded}',
    }

    code_payload = {
        'grant_type': 'refresh_token',
        'refresh_token': r_token,
    }
    response = requests.post(url=url, data=code_payload, headers=headers)
    data = response.json()

    return data['access_token']


def get_user_info(token):
    """Get the user info, the country information is needed for the current song."""
    try:
        url = 'https://api.spotify.com/v1/me'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url=url, headers=headers)
        data = response.json()

        user_country = data['country']

        return user_country
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def spotify_player(command, token):
    """Play next or previous song based on the command."""
    url = f'https://api.spotify.com/v1/me/player/{command}'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    try:
        response = requests.post(url=url, headers=headers)
        return response
    except Exception as e:
        logging.error(e, exc_info=True)


def spotify_pause(token):
    """Pause the current song."""
    url = 'https://api.spotify.com/v1/me/player/pause'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    try:
        response = requests.put(url=url, headers=headers)
        return response
    except Exception as e:
        logging.error(e, exc_info=True)


def spotify_play(token):
    """Play based on the saved song uri and progress."""
    url = 'https://api.spotify.com/v1/me/player/play'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    code_payload = {
        "uris": [session['uri']],
        "position_ms": session['progress']
    }

    try:
        response = requests.put(url=url, data=json.dumps(code_payload), headers=headers)
        return response
    except Exception as e:
        logging.error(e, exc_info=True)
