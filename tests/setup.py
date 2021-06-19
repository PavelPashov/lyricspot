"""Setup for E2E tests."""
import os

from src.spotify import get_refresh_token
from src.application import app

app = app

refresh_token = os.environ.get('REFRESH_TOKEN')

token = get_refresh_token(refresh_token)
