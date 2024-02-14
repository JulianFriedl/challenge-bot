import os
from dotenv import load_dotenv
from flask import Flask
from waitress import serve
import threading
import logging

# Import the strava_auth function
from controllers.strava_auth import strava_auth
from controllers.stats import stats

from config.log_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Register the strava_auth function as a route
app.route('/strava_auth')(strava_auth)
app.route('/stats')(stats)

def run():
    """
    Starts the Flask app.
    """
    serve(app, host='0.0.0.0', port=os.getenv("PORT"))

def start_flask():
    """
    Starts the Flask app in a new thread.
    """
    server = threading.Thread(target=run)
    server.start()
