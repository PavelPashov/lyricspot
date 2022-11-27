# Lyricspot

Fetches and displays lyrics for the currently playing song on your Spotify account

## Usage

Visit https://lyricspot.onrender.com and log in, no user details are saved

Note that a premium account is required for the player controlls

## Running locally

Python 3 is required

Clone the repo and run the below from the root directory:

`python -m pip install -r requirements.txt`

Then provide the following enveronmental variables:

`FLASK_APP=src/application.py`
`FLASK_ENV=development`
`MUSIXMATCH_API_KEY=your_key`
`GENIUS_API_KEY=your_key`
`CLIENT_ID=your_spotify_cliet_id`
`CLIENT_SECRET=your_spotify_cliet_secret`

Finally run `flask run`

## Running tests

Provide the following enveronmental variables:

`MUSIXMATCH_API_KEY=your_key`
`GENIUS_API_KEY=your_key`
`CLIENT_ID=your_spotify_cliet_id`
`CLIENT_SECRET=your_spotify_cliet_secret`
`REFRESH_TOKEN=a_refresh_token_provided_by_spotify`

And then run:

`pytest`

## Automation tests

This repo: https://github.com/EiTamOnya/lyricspot-selenium tests the production version for basic functionallity
