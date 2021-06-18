import logging
import time
import os

from flask import Flask, flash, redirect, render_template, request, jsonify, session
from flask_session import Session

from werkzeug.security import check_password_hash


from spotify import generate_authorize_url, generate_access_token_url, get_current_song, \
    get_user_info, refresh_token, spotify_player, spotify_pause, spotify_play
from toptracks import get_csv_path
from helpers import login_required
from lyrics import Lyrics
from zegami import create_collection, create_yaml_file, get_coll_id, delete_file, check_progress, publish_coll

app = Flask(__name__)

hash_pw = os.environ.get("PASSWORD")

# stuff used for session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    url = generate_authorize_url()
    if not session.get('token'):
        return render_template('login.html', url=url)
    else:
        return redirect('/home')


@app.route("/hello")
def hello():
    token = ''
    response = generate_access_token_url()
    token = response.json()['access_token']
    r_token = response.json()['refresh_token']

    country = get_user_info(token)
    session['country'] = country
    session['token'] = token
    session['r_token'] = r_token
    session['token_time'] = int(time.time())

    return redirect('/home')


@app.route("/home")
@login_required
@refresh_token
def home():

    return render_template('index.html')


@app.route("/lyrics")
@login_required
@refresh_token
def lyrics():
    lyrics = Lyrics()
    lyrics.get_song_lyrics(session['country'], session['token'])
    return lyrics.content


@app.route("/song")
@login_required
def songs():
    song = []
    try:
        song = get_current_song(session['country'], session['token'])
        if song is None:
            return None
        else:
            session['progress'] = song['progress']
            session['uri'] = song['uri']
        return jsonify(song)
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


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
        song = get_current_song(session['country'], session['token'])
        session['progress'] = song['progress']
        session['uri'] = song['uri']
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
