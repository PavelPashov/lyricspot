"""Class for returning song lyrics."""

import logging
import os
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, quote

from spotify import get_current_song

MUSIXMATCH_KEY = os.environ.get("MUSIXMATCH_API_KEY")
GENIUS_KEY = os.environ.get("GENIUS_API_KEY")


class Lyrics(object):
    """Class for the lyrics."""

    def __init__(self):
        """Constructor."""
        self.content = ''

    def find_song_musixmatch(self, song, artists):
        try:
            url = 'https://api.musixmatch.com/ws/1.1/track.search?'
            params = {
                'format': 'json',
                'q_track': song,
                'q_artist': artists,
                'quorum_factor': '1',
                'apikey': MUSIXMATCH_KEY
            }
            response = requests.get(url + urlencode(params))
            data = response.json()
            track_url = data['message']['body']['track_list'][0]['track']['track_share_url']
            track_url_obj = urlparse(track_url)
            return track_url_obj.path
        except Exception as e:
            logging.error(e, exc_info=True)
            return None

    def find_lyrics_musixmatch(self, song, artists):
        print('SEARCHING MUSIXMATCH!!!')
        if (path := self.find_song_musixmatch(song, artists)):
            print(path)
            try:
                url = f"https://www.musixmatch.com{path}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'
                }
                response = requests.get(url=url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.content, "html.parser")
                elements = soup.find_all(attrs={"class": "mxm-lyrics__content"})
                lyrics = ''
                for element in elements:
                    lyrics += element.text
                if lyrics != '':
                    self.content = lyrics
                else:
                    # This is for debugging
                    print(soup)
            except Exception as e:
                logging.error(e, exc_info=True)

    def find_song_genius(self, song, artist):
        try:
            url = 'http://api.genius.com/search?'
            params = {
                'q': song + ' ' + artist,
            }
            headers = {
                'Authorization': f'Bearer {GENIUS_KEY}'
            }
            response = requests.get(url=url + urlencode(params), headers=headers)
            data = response.json()
            for track in data['response']['hits']:
                if (track['result']['title'].lower() in song.lower() or
                        song.lower() in track['result']['full_title'].lower())\
                        and artist.lower() == track['result']['primary_artist']['name'].lower().strip():
                    return track['result']['path']
        except Exception as e:
            logging.error(e, exc_info=True)

    def find_lyrics_genius(self, song, artist):
        print('SEARCHING GENIOUS!!!')
        if (path := self.find_song_genius(song, artist)):
            print(path)
            pattern_letters = re.compile(r'([a-z]|[.?!;")\'}/])([A-Z])')
            pattern_brackets = re.compile(r'(\[\w.+\])')
            pattern_container = re.compile(r'(Lyrics__Container-sc.*)')
            try:
                URL = "http://genius.com" + path
                response = requests.get(url=URL)
                soup = BeautifulSoup(response.content, "html.parser")
                # doing this because genius provides 2 or more different pages randomly
                lyrics1 = soup.find("div", class_="lyrics")
                lyrics2 = soup.find_all("div", class_=pattern_container)
                if lyrics1:
                    lyrics = lyrics1.get_text()
                    self.content = lyrics
                elif lyrics2:
                    lyrics = ''.join([lyric.text for lyric in lyrics2])
                    lyrics = re.sub(pattern_letters, r'\1\n\2', lyrics)
                    lyrics = re.sub(pattern_brackets, r'\n\n\1\n', lyrics)
                    self.content = lyrics
            except Exception as e:
                logging.error(e, exc_info=True)

    # This is still broken, will check in the future
    def find_lyrics_ovh(self, song, artist):
        url = 'https://api.lyrics.ovh/v1/' + quote(f'{artist}/{song}')
        try:
            response = requests.get(url)
            if response.json()['lyrics']:
                return response.json()['lyrics']
            else:
                return None
        except Exception as e:
            logging.error(e, exc_info=True)
            return None

    def get_song_lyrics(self, country, token):
        song = get_current_song(country, token)
        artist = song['artists'][0]['name']

        google_href = 'https://www.google.com/search?q=' + quote(f"{song['name']} {artist} lyrics")
        lyrics_not_found = f'Lyrics not found :(\n<a href={google_href} target="_blank">Google it!</a>'

        self.find_lyrics_genius(song['name'], artist)
        if self.content == '':
            self.find_lyrics_musixmatch(song['name'], artist)
            if self.content == '':
                self.content = lyrics_not_found
