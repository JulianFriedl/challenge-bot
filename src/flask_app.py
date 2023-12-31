"""
file: flask_app.py

description: This script sets up and runs the Flask web server, which listens for incoming
authorization codes from the Strava API and passes them to the Discord bot.

Author: Julian Friedl
"""

from flask import Flask, request
from waitress import serve
import threading

import commands.strava_auth_command as StravaAuth

app = Flask(__name__)

@app.route('/strava_auth')
def strava_auth():
    """
    Handles incoming requests at the /strava_auth endpoint.

    This function is called when the user is redirected back to our application
    from the Strava authorization page after granting permission. It extracts
    the authorization code from the request and passes it to our Discord bot.
    """
    # Extract the authorization code from the request
    code = request.args.get('code')

    if code:
        # Pass the authorization code to our Discord bot
        try:
            StravaAuth.exchange_code(code)
            # Return a response to the user
            return 'Authorization successful! You can close this window.'
        except Exception as e:
            print(e)
            return 'An error occurred while processing the authorization. You can close this window.'
    else:
        return 'Authorization declined! You can close this window.'

def run():
    """
    Starts the Flask app.

    This function starts the Flask app and listens for incoming requests on port 8000.
    """
    serve(app, host='0.0.0.0', port=8000)

def start_flask():
    """
    Starts the Flask app in a new thread.

    This function starts the Flask app in a new thread so that it can run concurrently
    with our Discord bot.
    """
    server = threading.Thread(target=run)
    server.start()
