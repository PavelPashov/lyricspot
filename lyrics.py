"""functions used for finding and scraping lyrics"""

import logging
import os
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, quote

from spotify import get_current_song

musixmatch_key = os.environ.get("MUSIXMATCH_API_KEY")
genius_key = os.environ.get("GENIUS_API_KEY")


def get_song_url_musixmatch(song, artists):
    try:
        url = 'https://api.musixmatch.com/ws/1.1/track.search?'
        params = {
            'format': 'json',
            'q_track': song,
            'q_artist': artists,
            'quorum_factor': '1',
            'apikey': musixmatch_key
        }
        response = requests.get(url + urlencode(params))
        data = response.json()
        track_url = data['message']['body']['track_list'][0]['track']['track_share_url']
        track_url_obj = urlparse(track_url)
        return track_url_obj.path
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def find_lyrics_musixmatch(path):
    if path:
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
                return lyrics
            else:
                print(soup)
        except Exception as e:
            logging.error(e, exc_info=True)
            return None
    else:
        return None


def find_song_genius(song, artists):
    try:
        url = 'http://api.genius.com/search?'
        params = {
            'q': song + ' ' + artists,
        }
        headers = {
            'Authorization': f'Bearer {genius_key}'
        }
        response = requests.get(url=url + urlencode(params), headers=headers)
        data = response.json()
        for track in data['response']['hits']:
            if (track['result']['title'].lower() in song.lower() or
                song.lower() in track['result']['full_title'].lower())\
               and artists.lower() == track['result']['primary_artist']['name'].lower().strip():
                return track['result']['path']
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def find_lyrics_genius(path):
    if path:
        pattern_letters = re.compile(r'([a-z]|[.?!;")\'}/])([A-Z])')
        pattern_brackets = re.compile(r'(\[\w.+\])')
        try:
            URL = "http://genius.com" + path
            response = requests.get(url=URL)
            soup = BeautifulSoup(response.content, "html.parser")
            lyrics1 = soup.find("div", class_="lyrics")
            lyrics2 = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")
            if lyrics1:
                lyrics = lyrics1.get_text()
            elif lyrics2:
                # doing this because genius provides 2 different pages randomly
                lyrics = re.sub(pattern_letters, r'\1\n\2', lyrics2.get_text())
                lyrics = re.sub(pattern_brackets, r'\n\n\1\n', lyrics)
            elif lyrics1 == lyrics2 is None:
                lyrics = None
            return lyrics
        except Exception as e:
            logging.error(e, exc_info=True)
            return None
    else:
        return None

def find_lyrics_ovh(song, artist):
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


def get_song_lyrics(country, token):
    song = get_current_song(country, token)
    artist = song['artists'][0]['name']

    google_href = 'https://www.google.com/search?q=' + quote(f"{song['name']} {artist} lyrics")
    lyrics_not_found = f'Lyrics not found :(\n<a href={google_href} target="_blank">Google it!</a>'

    lyrics = find_lyrics_ovh(song['name'], artist)
    if lyrics:
        return lyrics
    else:
        path = find_song_genius(song['name'], artist)
        lyrics = find_lyrics_genius(path)
        if lyrics:
            print('genius.com', path)
            return lyrics
        else:
            path = get_song_url_musixmatch(song['name'], artist)
            lyrics = find_lyrics_musixmatch(path)
            if lyrics:
                print('musixmatch.com', path)
                return lyrics
            else:
                return lyrics_not_found
