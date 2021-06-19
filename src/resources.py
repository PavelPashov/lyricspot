"""API resouces."""
from flask import session
from flask_restful import Resource
from .utils import login_required
from .songs import CurrentSong, RecentSongs, TopSongs


class PlayingSongAPI(Resource):
    """Resource for getting the current song."""

    def current_song(self):
        self.song = CurrentSong()
        if self.song.is_playing:
            session['progress'] = self.song.progress
            session['uri'] = self.song.uri

    @login_required
    def get(self):
        self.current_song()
        if self.song.is_playing:
            return self.song.__dict__
        else:
            return '', 204


class RecentSongAPI(Resource):
    """Resource for getting a recent song."""

    def __init__(self):
        self.tracks = RecentSongs()

    @login_required
    def get(self, song_id):
        self.tracks.get_songs()
        return self.tracks.songs[int(song_id)].__dict__


class RecentSongLyricsAPI(RecentSongAPI):
    """Resource for getting a recent song."""

    @login_required
    def get(self, song_id):
        self.tracks.get_songs()
        self.tracks.songs[int(song_id)].get_song_lyrics()
        return self.tracks.songs[int(song_id)]._lyrics


class RecentSongsAPI(RecentSongAPI):
    """Resource for getting all recent songs."""

    @login_required
    def get(self):
        self.tracks.get_songs()
        return [song.__dict__ for song in self.tracks.songs]


class TopSongAPI(RecentSongAPI):
    """Resource for getting a top song."""

    def __init__(self):
        self.tracks = TopSongs()


class TopSongsAPI(RecentSongsAPI):
    """Resource for getting all top songs."""

    def __init__(self):
        self.tracks = TopSongs()


class TopSongLyricsAPI(RecentSongLyricsAPI):
    """Resource for getting a top song's lyrics."""

    def __init__(self):
        self.tracks = TopSongs()


class CurrentLyricsAPI(Resource):
    """Resource for getting the lyrics of the current song."""

    def lyrics(self):
        song = CurrentSong()
        song.check_for_cached_lyrics()

        return song._lyrics

    @login_required
    def get(self):
        return self.lyrics()
