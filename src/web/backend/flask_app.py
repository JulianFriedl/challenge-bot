import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from waitress import serve
import threading
import logging

# Import the strava_auth function
from src.web.backend.controllers.strava_auth import strava_auth
from src.web.backend.controllers.map import map
from src.web.backend.controllers.getAvailable import athletes, years

from src.shared.config.log_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Allow both localhost and 127.0.0.1, with and without port numbers, as origins
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:8000", "http://127.0.0.1:8000", "http://stravascape.site"]}})

# Register the strava_auth function as a route
app.route('/strava_auth')(strava_auth)
app.route('/api/map', methods=['GET'])(map)
app.route('/api/athletes', methods=['GET'])(athletes)
app.route('/api/years', methods=['GET'])(years)

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
