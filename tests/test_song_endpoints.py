"""E2E tests for the music player."""

import json
import requests
import time
from .setup import app, set_up_session, token


def check_song_endpoint(endpoint):
    """Check the status code and return the date of a given endpoint."""
    with app.test_client() as client:
        set_up_session(client)
        response = client.get(f'/api/v0/songs/{endpoint}')
        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 200
        return data


def test_get_recent_song():
    """Test for a single recent song."""
    data = check_song_endpoint('recetly_played/1')
    assert data['progress'] == 100
    assert data['is_playing'] is False


def test_get_recent_songs():
    """Test for all recent songs."""
    data = check_song_endpoint('recetly_played/')
    assert data[0]['progress'] == 100
    assert len(data) == 50


def test_get_top_song():
    """Test for a single top song."""
    data = check_song_endpoint('top/1')
    assert 'image_link' in data
    assert 'name' in data


def test_get_top_songs():
    """Test for all top songs."""
    data = check_song_endpoint('top/')
    assert 'name' in data[0]
    assert len(data) == 50


def spotify_play_song():
    url = 'https://api.spotify.com/v1/me/player/play'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    code_payload = {
        "context_uri": "spotify:album:2kyTLcEZe6nc1s6ve0zW9P",
        "offset": {
            "position": 4
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
        time.sleep(2)
        response = client.get('/api/v0/songs/current')
        print(response.data)
        data = json.loads(response.get_data(as_text=True))
        assert response.status_code == 200
        assert data['name'] == 'All Star'
        assert data['album'] == 'Astro Lounge'
