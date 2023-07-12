import requests
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import AuthDataController
import json

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRETE = os.getenv("CLIENT_SECRETE")
REDIRECT_URI = os.getenv("REDIRECT_URI")

def stravaAuth():
     #  Redirect the user to the Strava authorization page
        params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'approval_prompt': 'force',
            'scope': 'read,activity:read'
        }
        url = f'https://www.strava.com/oauth/authorize?{urlencode(params)}'

        return (f'Please click this link to authorize the bot to access your Strava data: {url}')
    
def exchange_code(code):
    # Exchange the authorization code for an access token
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRETE,
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post('https://www.strava.com/oauth/token', data=data)

    AuthDataController.save_credentials(response.text)
   