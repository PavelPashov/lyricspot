"""Class for the songs."""

import json
import logging
import requests

from flask import session

from .lyrics import Lyrics


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
        self.songs = []

    def recently_played_toJSON(self):
        """Parse the song to JSON."""
        return json.dumps(self.songs, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class RecentSongs(Songs):

    def get_songs(self, limit=50):
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
                song.image_link = item['track']['album']['images'][0]['url']
                song.link = item['track']['external_urls']['spotify']
                song.progress = 100
                song.is_playing = False
                self.songs.append(song)

        except Exception as e:
            logging.error(e, exc_info=True)
            return None


class TopSongs(Songs):

    def fetch_top(self, type='tracks', limit=50, term='long_term'):
        try:
            url = f'https://api.spotify.com/v1/me/top/{type}?time_range={term}&limit={limit}'

            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {session["token"]}',
            }
            response = requests.get(url=url, headers=headers)

            self.data = response.json()

        except Exception as e:
            logging.error(e, exc_info=True)
            return None

    def parse_top_songs(self):
        for item in self.data['items']:
            song = Song()
            song.album = item['album']['name']
            song.image_link = item['album']['images'][0]['url']
            song.date = item['album']['release_date']
            song.artists = []
            for artist in item['artists']:
                song.artists.append({'name': artist['name'], 'link': artist['external_urls']['spotify']})
            song.duration = item['duration_ms']
            song.song_id = item['id']
            song.name = item['name']
            song.link = item['external_urls']['spotify']
            song.popularity = item['popularity']
            self.songs.append(song)

    def get_songs(self, limit=50, term='long_term'):
        self.fetch_top(limit=50, term='long_term')
        self.parse_top_songs()
