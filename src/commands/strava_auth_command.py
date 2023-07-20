"""
strava_auth_command.py

This module contains functions for handling the strava_auth command

Author: Julian Friedl
"""

import requests
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import discord

import services.auth_data_controller as auth_data_controller

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRETE = os.getenv("CLIENT_SECRETE")
REDIRECT_URI = os.getenv("REDIRECT_URI")

def strava_auth():
    """
    Redirect the user to the Strava authorization page
    
    this function creates a link for the authorization with an embedded Link that leads back to my
    Webserver.
    """
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
         'approval_prompt': 'force',
         'scope': 'read,activity:read'
    }
    url = f'https://www.strava.com/oauth/authorize?{urlencode(params)}'

    embed = discord.Embed(title="Strava Authorization", 
                        description=f'Please click [this link]({url}) to authorize the bot to access your Strava data.', 
                        color=discord.Color.blue())
    return embed

#TODO add error handling
def exchange_code(code):
    """
    Exchanges the authorization code for an access token.
    This function takes the provided authorization code and exchanges it for an access token,
    then saves the credentials using the auth_data_controller.
    """
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRETE,
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post('https://www.strava.com/oauth/token', data=data)

    auth_data_controller.save_credentials(response.text)
   