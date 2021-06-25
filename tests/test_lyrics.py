"""E2E tests for the Lyrics class."""
import pytest
import time

from .setup import token, app
from src.lyrics import Lyrics
from src.songs import Song


song_name = "sunbather"
artist_name = "deafheaven"
song_lyrics = "always and forever"


def test_token():
    assert token != ""


def test_find_song_genius():
    lyrics = Lyrics()
    path = lyrics.find_song_genius(song_name, artist_name)
    for word in [song_name, artist_name, "lyrics"]:
        assert word in path.lower()


def test_get_song_genius():
    lyrics = Lyrics()
    lyrics.find_lyrics_genius(song_name, artist_name)
    actual_lyrics = lyrics._lyrics.lower()
    time.sleep(5)
    assert song_lyrics in actual_lyrics


def test_find_song_musixmatch():
    lyrics = Lyrics()
    path = lyrics.find_song_musixmatch(song_name, artist_name)
    for word in [song_name, artist_name, "lyrics"]:
        assert word in path.lower()


@pytest.mark.skip(reason="Failing in github actions")
def test_get_song_musixmatch():
    lyrics = Lyrics()
    lyrics.find_lyrics_genius(song_name, artist_name)
    assert song_lyrics in lyrics._lyrics.lower()


def test_get_song_lyrics():
    song = Song()
    song.name = song_name
    song.artists = [{"name": artist_name}]
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["lyrics"] = {"name": "", "artist": "", "lyrics": ""}
            with app.test_request_context():
                song.get_song_lyrics()
                assert song_lyrics in song._lyrics.lower()
