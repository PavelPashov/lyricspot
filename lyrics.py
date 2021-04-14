import logging
import os
import random
import requests

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urlencode, quote

from spotify import get_current_song

api_key = os.environ.get("MUSIXMATCH_API_KEY")

USER_AGENTS = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36']

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
        track_url_obj = urlparse(track_url)
        return track_url_obj.path
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def find_lyrics(url_obj):
    try:
        url = f"https://www.musixmatch.com{url_obj}"
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        req = requests.get(url=url, headers=headers, timeout=10, stream=True)
        soup = BeautifulSoup(req.content, "html.parser")
        elements = soup.find_all(attrs={"class": "mxm-lyrics__content"})
        lyrics = ''
        print(soup)
        print('Should be scraping')
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
        return response.json()['lyrics']
    except Exception as e:
        logging.error(e, exc_info=True)
        lyrics_url = get_song_url(song['name'], artists[0])
        lyrics = find_lyrics(lyrics_url)
        if lyrics:
            print('Getting lyrics from Musixmatch')
            return lyrics
        else:
            print('Scraped but no lyrics?!')
            return lyrics_not_found
    else:
        return lyrics_not_found
