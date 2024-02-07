"""
file: auth_data_controller.py

description: This module handles saving and loading credentials for the Discord bot.

Author: Julian Friedl
"""

import json
import os
import logging

from config.rules_preset import *
from config.log_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

SRC_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.dirname(SRC_PATH)
DATA_PATH = os.path.join(os.path.dirname(BASE_PATH), 'data')
FILENAME = os.path.join(DATA_PATH, 'credentials.json')


def save_strava_credentials(response: json = None, discord_user_id: str = None):
    """
    Saves user credentials to a file.

    This function takes a JSON string containing user credentials, 
    checks if a file for the user already exists, and either appends to or overwrites the file.
    """
    logger.info("Saving Credentials.")
    json_response = json.loads(response)

    athlete_constants = {
        "rules": RULES,
        "points_required": POINTS_REQUIRED,
        "price_per_week": PRICE_PER_WEEK,
        "spazi": SPAZI,
        "walking_limit": WALKING_LIMIT,
        "hit_required": HIT_REQUIRED,
        "hit_min_time": HIT_MIN_TIME,
        "min_duration_multi_day": MIN_DURATION_MULTI_DAY,
        "start_week": CHALLENGE_START_WEEK,
    }

    athlete_vars = {
        "joker": JOKER,
        "joker_weeks": [],
        "week_results": []
    }

    credentials = {}
    if 'strava_data' in json_response:
        credentials['strava_data'] = json_response['strava_data']
    else:
        credentials['strava_data'] = json_response
    credentials['constants'] = athlete_constants
    credentials['vars'] = athlete_vars
    credentials['discord_user_id'] = discord_user_id

    data = load_or_create_data_dir()

    # Update or append the new credentials
    for existing_cred in data:
        if existing_cred['strava_data']['athlete']['id'] == credentials['strava_data']['athlete']['id']:
            existing_cred['strava_data'] = credentials['strava_data']
            if credentials['discord_user_id']:
                existing_cred['discord_user_id'] = credentials['discord_user_id']
            break
    else:
        data.append(credentials)

    with open(FILENAME, 'w') as f:
        json.dump(data, f, default=serialize, indent=4)


def update_athlete_vars(credentials: dict):
    data = load_or_create_data_dir()
    for existing_cred in data:
        if existing_cred['strava_data']['athlete']['id'] == credentials['strava_data']['athlete']['id']:
            if credentials['vars']:
                existing_cred['vars'] = credentials['vars']
            break
    with open(FILENAME, 'w') as f:
        json.dump(data, f, default=serialize, indent=4)


def load_or_create_data_dir():
    # Create the data directory if it doesn't exist
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    # Load existing data or initialize it
    if os.path.exists(FILENAME) and os.path.getsize(FILENAME) > 0:
        with open(FILENAME, 'r') as file:
            data = json.load(file)
    else:
        data = []

    return data


def load_credentials():
    """
    Loads user credentials from a file.

    This function checks if a file with user credentials exists, and if so, loads and returns the credentials.
    """
    if os.path.exists(FILENAME) and os.path.getsize(FILENAME) != 0:
        with open(FILENAME, 'r') as f:
            credentials = json.load(f)
        return credentials
    return None


def serialize(obj):
    """
    Serializes an object to be saved to a file.

    This function converts set and bytes objects to lists and strings respectively, 
    and recursively applies itself to elements of dictionaries, lists, and tuples.
    """
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    elif isinstance(obj, dict):
        return {str(k): serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize(i) for i in obj]
    else:
        return obj
