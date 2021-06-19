import logging
import time
import os

from flask import Flask,  redirect, render_template, request,  session
from flask_restful import Api
from flask_session import Session

from werkzeug.security import check_password_hash

from src.spotify import (
    generate_authorize_url,
    generate_access_token_url,
    get_user_info,
    spotify_player,
    spotify_pause,
    spotify_play
)

from src.songs import Song
from src.toptracks import get_csv_path
from src.utils import login_required, refresh_token
from src.resources import (
    CurrentLyricsAPI,
    PlayingSongAPI,
    RecentSongAPI,
    RecentSongLyricsAPI,
    RecentSongsAPI,
    TopSongAPI,
    TopSongsAPI,
    TopSongLyricsAPI
)

from src.zegami import (
    create_collection,
    create_yaml_file,
    get_coll_id, delete_file,
    check_progress,
    publish_coll
)

app = Flask(__name__)
api = Api(app)

hash_pw = os.environ.get("PASSWORD")

# stuff used for session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@refresh_token
@app.route("/")
def index():
    url = generate_authorize_url()
    if not session.get('token'):
        return render_template('login.html', url=url)
    else:
        return render_template('index.html')


@app.route("/hello")
def hello():
    token = ''
    response = generate_access_token_url()
    token = response.json()['access_token']
    r_token = response.json()['refresh_token']

    country = get_user_info(token)
    session['country'] = country
    session['lyrics'] = {'name': '', 'artist': '', 'lyrics': ''}
    session['token'] = token
    session['r_token'] = r_token
    session['token_time'] = int(time.time())

    return redirect('/')


api.add_resource(CurrentLyricsAPI, '/api/v0/songs/lyrics')
api.add_resource(PlayingSongAPI, '/api/v0/songs/current')
api.add_resource(RecentSongAPI, '/api/v0/songs/recetly_played/<string:song_id>')
api.add_resource(RecentSongLyricsAPI, '/api/v0/songs/recetly_played/lyrics/<string:song_id>')
api.add_resource(RecentSongsAPI, '/api/v0/songs/recetly_played/all')
api.add_resource(TopSongAPI, '/api/v0/songs/top/<string:song_id>')
api.add_resource(TopSongsAPI, '/api/v0/songs/top/all')
api.add_resource(TopSongLyricsAPI, '/api/v0/songs/top/lyrics/<string:song_id>')


@app.route('/player', methods=['POST'])
@login_required
@refresh_token
def player():
    if request.method == "POST":
        response = spotify_player(request.form['option'], session['token'])
        return '', response.status_code


@app.route('/pause', methods=['POST'])
@login_required
@refresh_token
def pause():
    if request.method == "POST":
        song = Song()
        song.get_current_song()
        session['progress'] = song.progress
        session['uri'] = song.uri
        response = spotify_pause(session['token'])
        return '', response.status_code


@app.route('/play', methods=['POST'])
@login_required
@refresh_token
def play():
    if request.method == "POST":
        response = spotify_play(session['token'])
        return '', response.status_code


@app.route('/mode', methods=['POST'])
@login_required
@refresh_token
def mode():
    if request.method == "POST":
        try:
            if request.form['option'] == 'dark':
                session['mode'] = {'link': '../static/darkstyles.css', 'name': 'dark'}
            else:
                session['mode'] = {'link': '../static/lightstyles.css', 'name': 'light'}
            return session['mode']
        except Exception as e:
            logging.error(e, exc_info=True)
            return None


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/check', methods=['POST'])
@login_required
def check():
    if request.method == "POST":
        try:
            progress = check_progress(session['coll_id'])
            progress = progress * 80
            if progress == 80 and session['is_published'] is True:
                progress = check_progress(session['coll_id'], project='public')
                progress = int(progress * 20) + 80
            if check_progress(session['coll_id']) == 1 and session['is_published'] is False:
                publish_coll(session['coll_id'])
            return str(int(progress))
        except Exception as e:
            logging.error(e, exc_info=True)
            return None


@app.route('/publish', methods=["POST"])
@login_required
def publish():
    if request.method == "POST":
        publish_coll(session['coll_id'])


@app.route('/collection', methods=["GET", "POST"])
@login_required
def collection():
    if request.method == "POST":
        coll_name = request.form['coll_name']
        password = request.form['password']
        session['is_published'] = False
        if check_password_hash(hash_pw.strip("'"), password):
            csv_path = get_csv_path('long_term')
            yaml_path = create_yaml_file(str(coll_name), csv_path)
            coll_id = get_coll_id(create_collection(yaml_path))
            delete_file([yaml_path, csv_path])
            session['coll_id'] = coll_id
            coll_url = f'https://staging.zegami.com/collections/public-{coll_id}'
            message = "Creating your collection!"
            return render_template('progress.html', coll_url=coll_url, message=message)
        else:
            message = "Wrong password, please try again!"
            return render_template('progress.html', message=message)
    else:
        return render_template('collection.html')
