import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRETE = os.getenv("CLIENT_SECRETE")
REDIRECT_URI = os.getenv("REDIRECT_URI")

def refresh_token(cred):
    # Get the access token, refresh token and expiration date from the credential dictionary
    access_token = cred["access_token"]
    refresh_token = cred["refresh_token"]
    expires_at = cred["expires_at"]

    # Get the current time in seconds
    current_time = time.time()

    # Check if the access token is expired or will expire soon
    if current_time > expires_at - 60:
        # The access token is expired or will expire soon, so we need to refresh it
        print("Refreshing token...")

        # Set up the data for the api call
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRETE,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        # Print out the data for debugging
        print(f"Data: {data}")

        # Make the api call to get a new access token
        response = requests.post('https://www.strava.com/oauth/token', data=data)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the response data as a dictionary
            data = response.json()

            # Get the new access token, refresh token and expiration date from the response data
            new_access_token = data["access_token"]
            new_refresh_token = data["refresh_token"]
            new_expires_at = data["expires_at"]

            # Update the credential dictionary with the new values
            cred["access_token"] = new_access_token
            cred["refresh_token"] = new_refresh_token
            cred["expires_at"] = new_expires_at

            print("Token refreshed successfully.")
        else:
            # Handle unsuccessful response
            print(f"Error: Could not refresh token. Status code: {response.status_code}")
    else:
        # The access token is still valid, so we don't need to refresh it
        print("Token is still valid.")

    return cred
