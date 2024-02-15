import os
import requests
import time
import logging

from dotenv import load_dotenv
from src.shared.config.log_config import setup_logging


setup_logging()
logger = logging.getLogger(__name__)
load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRETE = os.getenv('STRAVA_CLIENT_SECRETE')

def refresh_token(cred:dict):
    # Get the access token, refresh token and expiration date from the credential dictionary
    refresh_token = cred['strava_data']['refresh_token']
    expires_at = cred['strava_data']['expires_at']

    # Get the current time in seconds
    current_time = time.time()

    # Check if the access token is expired or will expire soon
    if current_time > expires_at - 60:
        # The access token is expired or will expire soon, so we need to refresh it
        logger.info("Refreshing token...")

        # Set up the data for the api call
        data = {
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRETE,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        # Make the api call to get a new access token
        response = requests.post('https://www.strava.com/oauth/token', data=data)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the response data as a dictionary
            data = response.json()

            # Get the new access token, refresh token and expiration date from the response data
            new_access_token = data['access_token']
            new_refresh_token = data['refresh_token']
            new_expires_at = data['expires_at']

            # Update the credential dictionary with the new values
            cred['strava_data']['access_token'] = new_access_token
            cred['strava_data']['refresh_token'] = new_refresh_token
            cred['strava_data']['expires_at'] = new_expires_at

            logger.info("Token refreshed successfully.")
        else:
            # Handle unsuccessful response
            logger.error(f"Error: Could not refresh token. Status code: {response.status_code}")
    else:
        # The access token is still valid, so we don't need to refresh it
        logger.info("Token is still valid.")

    return cred
