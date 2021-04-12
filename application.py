import os
import logging
from flask import Flask, flash, redirect, render_template, request, jsonify, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import json
import requests
import base64
import time
from urllib.parse import urlparse, urlencode, quote

from spotify import generate_authorize_url, generate_access_token_url, get_current_song, get_recently_played_songs, \
    get_user_info, refresh_token, spotify_player, spotify_pause, spotify_play
from helpers import login_required
from lyrics import get_song_lyrics

app = Flask(__name__)

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
        return render_template('index.html')

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
def home():

    return render_template('index.html')

@app.route("/lyrics")
@login_required
@refresh_token
def lyrics():
    lyrics = get_song_lyrics(session['country'], session['token'])
    return lyrics

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

@app.route('/last')
@login_required
def last():
    songs = get_recently_played_songs(5, session['token'])
    if songs:
        return jsonify(songs)
    
@app.route('/player', methods = ['POST'])
@login_required
@refresh_token
def player():
    if request.method == "POST":
        response = spotify_player(request.form['option'], session['token'])
        return '', response.status_code

@app.route('/pause', methods = ['POST'])
@login_required
@refresh_token
def pause():
    if request.method == "POST":
        song = get_current_song(session['country'], session['token'])
        session['progress'] = song['progress']
        session['uri'] = song['uri']
        response = spotify_pause(session['token'])
        return '', response.status_code

@app.route('/play', methods = ['POST'])
@login_required
@refresh_token
def play():
    if request.method == "POST":
        response = spotify_play(session['token'])
        return '', response.status_code

@app.route('/mode', methods = ['POST'])
@login_required
@refresh_token
def mode():
    if request.method == "POST":
        try:
            if request.form['option'] == 'dark':
                session['mode'] = {'link': '../static/darkstyles.css', 'name': 'dark'}
            else:
                session['mode'] = {'link':'../static/lightstyles.css', 'name': 'light'}
            return session['mode']
        except Exception as e:
            logging.error(e, exc_info=True)
            return None
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')