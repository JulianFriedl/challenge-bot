from flask import Flask, request
from waitress import serve
import threading
import commands.StravaAuthCommand as StravaAuth

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

    if(code != None):
        # Pass the authorization code to our Discord bot
        StravaAuth.exchange_code(code)
         # Return a response to the user
        return 'Authorization successful! You can close this window.'
    else:
        return 'Authorization declined! You can close this window.'

   

def run():
    """
    Starts the Flask app.

    This function starts the Flask app and listens for incoming requests on port 8000.
    """
    serve(app, host='0.0.0.0', port=8000)

def startFlask():
    """
    Starts the Flask app in a new thread.

    This function starts the Flask app in a new thread so that it can run concurrently
    with our Discord bot.
    """
    server = threading.Thread(target=run)
    server.start()

