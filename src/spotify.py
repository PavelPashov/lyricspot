from flask import request, session
from urllib.parse import urlencode
from .lyrics import Lyrics

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

REDIRECT_URI = 'https://lyric-spot.herokuapp.com/hello'

if FLASK_ENV == 'development':
    REDIRECT_URI = 'http://127.0.0.1:5000/hello'


def generate_authorize_url():
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
    }

    return f'{SPOTIFY_AUTH_URL}?{urlencode(params)}'


def generate_access_token_url():
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


class Song(Lyrics):
    """Class for Songs."""

    def parse_current_song_data(self, data):
        """Get the data from the spotify endpoint, parse and assign attributes."""
        artists = []
        for artist in data['item']['artists']:
            artists.append({'name': artist['name'], 'link': artist['external_urls']['spotify']})
        self.name = data['item']['name']
        self.artists = artists
        self.album = data['item']['album']['name']
        self.link = data['item']['external_urls']['spotify']
        self.progress = data['progress_ms']
        self.duration = data['item']['duration_ms']
        self.uri = data['item']['uri']
        self.is_playing = data['is_playing']
        self.image_link = data['item']['album']['images']

    def get_current_song(self):
        """Get the song playing currently."""
        try:
            url = 'https://api.spotify.com/v1/me/player/currently-playing'
            headers = {
                'market': session['country'],
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {session["token"]}',
            }

            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                self.parse_current_song_data(response.json())
        except Exception as e:
            logging.error(e, exc_info=True)

    def toJSON(self):
        """Parse the song to JSON."""
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class CurrentSong(Song):
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.get_current_song()


class Songs(Song):

    def __init__(self):
        self.recently_played = []

    def get_recently_played_songs(self, limit):
        """Get all recentely played songs."""
        try:
            url = f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}'

            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {session["token"]}',
            }
            response = requests.get(url=url, headers=headers)
            data = response.json()
            for item in data['items']:
                song = Song()
                song.name = item['track']['name']
                artists = []
                for artist in item['track']['artists']:
                    artists.append({'name': artist['name'], 'link': artist['external_urls']['spotify']})
                song.artists = artists
                song.album = item['track']['album']['name']
                song.duration = item['track']['duration_ms']
                song.link = item['track']['external_urls']['spotify']
                song.progress = 100
                song.is_playing = False
                self.recently_played.append(song)
        except Exception as e:
            logging.error(e, exc_info=True)
            return None

    def recently_played_toJSON(self):
        """Parse the song to JSON."""
        return json.dumps(self.recently_played, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def spotify_player(command, token):
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
