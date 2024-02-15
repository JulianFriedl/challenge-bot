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

from src.shared.api.custom_api_error import CustomAPIError
class API_CALL_TYPE(Enum):
    Cache = 1
    API = 2
    Error = 3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CACHE_PATH = os.path.join(PROJECT_ROOT, 'cache')
os.makedirs(CACHE_PATH, exist_ok=True)  # make sure the directory exists

def api_request(url:str, headers:dict, params:dict, username:str, user_id:str, cache:bool = True):
    """
    Makes a GET request to the specified URL and handles HTTP errors.

    This function makes a GET request to the specified URL with the provided headers and parameters.
    If the request is successful, it returns the JSON response and None as error embed.
    If the request fails, it returns None and a Discord embed with the appropriate error message.

    Args:
        url (str): The URL to make the request to.
        headers (dict, optional): The headers for the request.
        params (dict, optional): The parameters for the request.
        username (str): The username for the request.
        id(str): the id of the user, used for encoding the cache with a unique filename

    Returns:
        response (dict or None): The JSON response if the request was successful, otherwise None.
        API_CALL_TYPE (Cache = 1 API = 2, Error = 3): Cache if the cache is used and API if the api is used and Error if error occurs
    """
       #check if the cache dir exists
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
        
    if cache:
    # Create a hash of the url, headers and params to uniquely identify the request
        req_hash = hashlib.sha256() 
        req_hash.update(url.encode('utf-8'))
        #req_hash.update(str(headers).encode('utf-8'))
        #I am leaving out the headers because the auth token changes every 6 hours, so that would mean the cache expires at the same rate
        #But to still be able to uniquely identify each cache file i will include the uid in the hash
        req_hash.update(str(user_id).encode('utf-8'))
        req_hash.update(str(params).encode('utf-8'))
        cache_file = os.path.join(CACHE_PATH, req_hash.hexdigest())
        # If the cache file exists, load the cached response
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f), API_CALL_TYPE.Cache
        
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        
        if cache:
            # Cache the response
            with open(cache_file, 'wb') as f:
                pickle.dump(response.json(), f)

        return response.json(), API_CALL_TYPE.API
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
        raise CustomAPIError(message, error_embed) from e
    except requests.exceptions.RequestException as e:
        message = f"An error occurred while making the API request for user {username}: {str(e)}"
        error_embed = discord.Embed(title="Request Error", description=message, color=discord.Color.red())
        raise CustomAPIError(message, error_embed) from e
