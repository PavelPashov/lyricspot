from flask import Flask, request, session
from urllib.parse import urlparse, urlencode, quote
from functools import wraps

import base64
import json
import logging
import os
import time
import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

SCOPE = 'user-read-email user-read-recently-played \
        user-read-recently-played user-read-playback-state user-read-currently-playing user-read-private \
        user-modify-playback-state'

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = 'v1'

data_bytes = f'{CLIENT_ID}:{CLIENT_SECRET}'

encoded = base64.urlsafe_b64encode(data_bytes.encode()).decode()

REDIRECT_URI = 'http://127.0.0.1:5000/hello'

def generate_authorize_url():
    params={
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

def get_current_song(country_code, token):
    try:
        url = 'https://api.spotify.com/v1/me/player/currently-playing'
        
        headers = {
            'market': country_code,
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        
        response = requests.get(url=url, headers=headers)
        data = response.json()
        return parse_current_song_data(data)
    except Exception as e:
        logging.error(e, exc_info=True)
        return None

def get_recently_played_songs(limit, token):
    try:
        url = f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}'
        
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        
        response = requests.get(url=url, headers=headers)
        data = response.json()
        songs = []
        for item in data['items']:
            mydict = {}
            mydict['name'] = item['track']['name']
            artists = []
            for artist in item['track']['artists']:
                artists.append({'name': artist['name'], 'link': artist['external_urls']['spotify']})
            mydict['artists'] = artists
            mydict['duration'] = item['track']['duration_ms']
            mydict['link'] = item['track']['external_urls']['spotify']
            mydict['progress'] = 100
            mydict['is_playing'] = False
            songs.append(mydict)
        return songs
    except Exception as e:
        logging.error(e, exc_info=True)
        return None

def parse_current_song_data(data):
    song = {}
    artists = []
    for artist in data['item']['artists']:
        artists.append({'name': artist['name'], 'link': artist['external_urls']['spotify']})
    song['name'] = data['item']['name']
    song['artists'] = artists
    song['link'] = data['item']['external_urls']['spotify']
    song['progress'] = data['progress_ms']
    song['duration'] = data['item']['duration_ms']
    song['uri'] = data['item']['uri']
    song['is_playing'] = data['is_playing']
    song['image_link'] = data['item']['album']['images']
    return song

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
        
def refresh_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r_token = session.get('r_token')
        token_time = session.get('token_time')
        if int(token_time) + 3000 > int(time.time()):
            session['token'] = get_refresh_token(r_token)
            session['token_time'] = int(time.time())
        return f(*args, **kwargs)
    return decorated_function

def spotify_pause(token):
    url = f'https://api.spotify.com/v1/me/player/pause'
    
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
    url = f'https://api.spotify.com/v1/me/player/play'
    
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