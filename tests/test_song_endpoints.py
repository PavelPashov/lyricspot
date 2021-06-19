"""E2E tests for the music player."""

import json
import requests
import time
from .setup import app, set_up_session, token


def test_get_recent_song():
    with app.test_client() as client:
        set_up_session(client)
        responce = client.get('/api/v0/songs/recetly_played/1')
        data = json.loads(responce.get_data(as_text=True))
        assert responce.status_code == 200
        assert data['progress'] == 100
        assert data['is_playing'] is False


def test_get_recent_songs():
    with app.test_client() as client:
        set_up_session(client)
        responce = client.get('/api/v0/songs/recetly_played/all')
        data = json.loads(responce.get_data(as_text=True))
        assert responce.status_code == 200
        assert data[0]['progress'] == 100
        assert len(data) == 50


def spotify_play_song():
    url = 'https://api.spotify.com/v1/me/player/play'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    code_payload = {
        "context_uri": "spotify:album:2kKXGWaCEl06EKZ4DxBJIT",
        "offset": {
            "position": 2
        },
        "position_ms": 0
    }
    try:
        requests.put(url=url, data=json.dumps(code_payload), headers=headers)
    except Exception as ex:
        print(ex)


def test_get_current_song():
    spotify_play_song()
    with app.test_client() as client:
        set_up_session(client)
        # Fails without the wait
        time.sleep(1)
        responce = client.get('/api/v0/songs/current')
        print(responce.data)
        data = json.loads(responce.get_data(as_text=True))
        assert responce.status_code == 200
        assert data['name'] == 'Sunbather'
        assert data['album'] == 'Sunbather'
