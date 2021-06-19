
import logging
import requests
import tempfile

from flask import session


def get_top(type, limit, token, term):
    try:
        url = f'https://api.spotify.com/v1/me/top/{type}?time_range={term}&limit={limit}'

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url=url, headers=headers)
        data = response.json()\

        return data
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def parse_top_songs(data):
    songs = []
    artists = []
    song = {}
    for song in data['items']:
        album = song['album']['name']
        image_link = song['album']['images'][0]['url']
        date = song['album']['release_date']
        artists = []
        for artist in song['artists']:
            artists.append({'name': artist['name']})
        duration = song['duration_ms']
        song_id = song['id']
        name = song['name']
        popularity = song['popularity']

        song = {
            'album': album,
            'image_link': image_link,
            'date': date,
            'artists': artists,
            'duration': duration,
            'id': song_id,
            'name': name,
            'popularity': popularity
        }

        songs.append(song)
    return songs


def get_track_ids(data):
    items = []
    for item in data['items']:
        items.append(item['id'])

    return items


def get_track_features(track_list):
    try:
        songs_str = ",".join(track_list)
        url = 'https://api.spotify.com/v1/audio-features?ids=' + songs_str

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {session["token"]}',
        }

        response = requests.get(url=url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def assign_feauters_to_tracks(features, tracks):
    for song in tracks:
        for feature in features['audio_features']:
            if song['id'] == feature['id']:
                song['features'] = feature
    path = convert_data_to_csv(tracks)
    return tracks


def convert_data_to_csv(tracks):
    temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    path_to_csv = temp_csv.name
    keys = []
    for key in tracks[0].keys():
        if key != 'features':
            keys.append(key)

    for key in tracks[0]['features'].keys():
        if key not in ['analysis_url', 'id', 'track_href', 'type', 'duration_ms']:
            keys.append(key)

    with open(path_to_csv, 'a', encoding="utf-8") as f:
        f.write(','.join(keys) + '\n')

    with open(path_to_csv, 'a', encoding="utf-8") as f:
        for track in tracks:
            for item in track:
                artists = []
                features = []
                if item == 'features':
                    for feature in track['features']:
                        if feature not in ['analysis_url', 'id', 'track_href', 'type', 'duration_ms']:
                            features.append(str(track['features'][feature]))
                    f.write(','.join(features))
                elif item == 'artists':
                    for artist in track[item]:
                        artists.append(artist['name'])
                    f.write(f"\"{','.join(artists)}\",")
                elif item in ['name', 'album']:
                    f.write(str(track[item]).replace(',', ' ') + ',')
                else:
                    f.write(str(track[item]) + ',')
            f.write('\n')

    return path_to_csv


def get_csv_path(term):
    raw_songs = get_top('tracks', 50, session['token'], term)
    songs_ids = get_track_ids(raw_songs)
    songs = parse_top_songs(raw_songs)
    features = get_track_features(songs_ids)
    songs_with_features = assign_feauters_to_tracks(features, songs)
    csv_file_path = convert_data_to_csv(songs_with_features)
    return csv_file_path
