"""
api_error_handling.py

This module contains a function for making API requests and handling HTTP errors.

Author: Julian Friedl
"""

import hashlib
import os
import pickle
import requests
import discord
from enum import Enum

class API_CALL_TYPE(Enum):
    Cache = 1
    API = 2
    Error = 3


CACHE_DIR = './cache'
os.makedirs(CACHE_DIR, exist_ok=True)  # make sure the directory exists

def api_request(url, headers=None, params=None, username=None):
    """
    Makes a GET request to the specified URL and handles HTTP errors.

    This function makes a GET request to the specified URL with the provided headers and parameters.
    If the request is successful, it returns the JSON response and None as error embed.
    If the request fails, it returns None and a Discord embed with the appropriate error message.

    Args:
        url (str): The URL to make the request to.
        username (str): The username for the request.
        headers (dict, optional): The headers for the request.
        params (dict, optional): The parameters for the request.

    Returns:
        response (dict or None): The JSON response if the request was successful, otherwise None.
        error_embed (discord.Embed or None): None if the request was successful, otherwise a Discord embed with the error message.
        API_CALL_TYPE (Cache = 1 API = 2, Error = 3): Cache if the cache is used and API if the api is used and Error if error occurs
    """
    
    # Create a hash of the url, headers and params to uniquely identify the request
    req_hash = hashlib.md5()
    req_hash.update(url.encode('utf-8'))
    req_hash.update(str(headers).encode('utf-8'))
    req_hash.update(str(params).encode('utf-8'))
    cache_file = os.path.join(CACHE_DIR, req_hash.hexdigest())

    # If the cache file exists, load the cached response
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f), None, API_CALL_TYPE.Cache

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        # Cache the response
        with open(cache_file, 'wb') as f:
            pickle.dump(response.json(), f)

        return response.json(), None, API_CALL_TYPE.API
    except requests.exceptions.HTTPError as e:
        status_code = response.status_code

        # Customize the error messages for different status codes
        if status_code == 400:
            message = f"Bad Request for user {username}: The request was unacceptable, often due to a missing parameter."
        elif status_code == 401:
            message = f"Unauthorized for user {username}: Access token was missing or invalid."
        elif status_code == 403:
            message = f"Forbidden for user {username}: The request is understood, but it has been refused by the Strava API."
        elif status_code == 404:
            message = f"Not Found for user {username}: The requested resource could not be found."
        elif status_code == 429:
            message = f"Too Many Requests for user {username}: Rate limit exceeded, Wait 15 min."
        elif status_code == 500:
            message = f"Internal Server Error for user {username}: Strava had an error, try again later."
        else:
            message = f"An error occurred while making the API request for user {username}. Status code: {status_code}"

        error_embed = discord.Embed(title="HTTP Error", description=message, color=discord.Color.red())
        return None, error_embed, API_CALL_TYPE.Error
    except requests.exceptions.RequestException as e:
        message = f"An error occurred while making the API request for user {username}: {str(e)}"
        error_embed = discord.Embed(title="Request Error", description=message, color=discord.Color.red())
        return None, error_embed, API_CALL_TYPE.Error
