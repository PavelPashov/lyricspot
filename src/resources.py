"""API resouces."""
from flask import session
from flask_restful import Resource
from .utils import login_required
from .spotify import CurrentSong, Songs


class PlayingSong(Resource):
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


class RecentSong(Resource):
    """Resource for getting a recent song."""

    def get_songs(self):
        songs = Songs()
        songs.get_recently_played_songs(50)
        self.recent_songs = songs.recently_played

    @login_required
    def get(self, song_id):
        self.get_songs()
        return self.recent_songs[int(song_id)].__dict__


class RecentSongLyrics(RecentSong):
    """Resource for getting a recent song."""

    @login_required
    def get(self, song_id):
        self.get_songs()
        self.recent_songs[int(song_id)].get_song_lyrics()
        return self.recent_songs[int(song_id)]._lyrics


class RecentSongs(Resource):
    """Resource for getting all recent songs."""

    def get_songs(self):
        songs = Songs()
        songs.get_recently_played_songs(50)
        self.recent_songs = songs.recently_played

    @login_required
    def get(self):
        self.get_songs()
        return [song.__dict__ for song in self.recent_songs]


class CurrentLyrics(Resource):
    """Resource for getting the lyrics of the current song."""

    def lyrics(self):
        song = CurrentSong()
        song.check_for_cached_lyrics()

        return song._lyrics

    @login_required
    def get(self):
        return self.lyrics()
