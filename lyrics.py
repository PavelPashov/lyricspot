''' code for fetchign lyrics '''

import logging
import os
import requests

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urlencode, quote

from spotify import get_current_song

api_key = os.environ.get("MUSIXMATCH_API_KEY")


def get_song_url(song, artists):
    try:
        url = 'https://api.musixmatch.com/ws/1.1/track.search?'
        params = {
            'format': 'json',
            'q_track': song,
            'q_artist': artists,
            'quorum_factor': '1',
            'apikey': api_key
        }
        response = requests.get(url + urlencode(params))
        data = response.json()
        track_url = data['message']['body']['track_list'][0]['track']['track_share_url']
        is_instrumental = data['message']['body']['track_list'][0]['track']['instrumental']
        if is_instrumental == 0:
            track_url_obj = urlparse(track_url)
            return track_url_obj.path
        elif is_instrumental == 1:
            return 'instrumental'
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def find_lyrics(url_obj):
    try:
        url = f"https://www.musixmatch.com{url_obj}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=url, headers=headers)
        html_bytes = urlopen(req).read()
        html = html_bytes.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(attrs={"class": "mxm-lyrics__content"})
        lyrics = ''
        for element in elements:
            lyrics += element.text
        return lyrics
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def get_song_lyrics(country, token):
    song = get_current_song(country, token)
    artists = []
    for artist in song['artists']:
        artists.append(artist['name'])

    google_href = 'https://www.google.com/search?q=' + \
        quote(f"{song['name']} {' '.join(artists)} lyrics")
    lyrics_not_found = f'Lyrics not found :(\n<a href={google_href} target="_blank">Google it!</a>'

    url = 'https://api.lyrics.ovh/v1/' + \
        quote(f'{artists[0]}/{song["name"]}')
    try:
        response = requests.get(url)
        if response.json()['lyrics']:
            return response.json()['lyrics']
    except Exception as e:
        logging.error(e, exc_info=True)
        lyrics_url = get_song_url(song['name'], artists[0])
        lyrics = find_lyrics(lyrics_url)
        if lyrics:
            return lyrics
        else:
            return lyrics_not_found
    else:
        return lyrics_not_found
