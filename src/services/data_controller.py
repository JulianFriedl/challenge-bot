"""
file: auth_data_controller.py

description: This module handles saving and loading credentials for the Discord bot.

Author: Julian Friedl
"""

import datetime
import json
import os
import logging

from config.rules_preset import *
from config.log_config import setup_logging
from threading import Lock

from models.activity import Activity
from models.athlete import Athlete

file_lock = Lock()  # locking mechanism for threading


setup_logging()
logger = logging.getLogger(__name__)

SRC_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.dirname(SRC_PATH)
DATA_PATH = os.path.join(os.path.dirname(BASE_PATH), 'data')
CREDENTIALS = os.path.join(DATA_PATH, 'credentials.json')
ROUTES = os.path.join(DATA_PATH, 'routes.json')


def save_strava_credentials(response: json = None, discord_user_id: str = None):
    """
    Saves user credentials to a file.

    This function takes a JSON string containing user credentials, 
    checks if a file for the user already exists, and either appends to or overwrites the file.
    """
    with file_lock:
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

        data = load_or_create_credentials()

        # Update or append the new credentials
        for existing_cred in data:
            if existing_cred['strava_data']['athlete']['id'] == credentials['strava_data']['athlete']['id']:
                existing_cred['strava_data'] = credentials['strava_data']
                if credentials['discord_user_id']:
                    existing_cred['discord_user_id'] = credentials['discord_user_id']
                break
        else:
            data.append(credentials)

        with open(CREDENTIALS, 'w') as f:
            json.dump(data, f, default=serialize, indent=4)


def update_athlete_vars(credentials: dict):
    with file_lock:
        data = load_or_create_credentials()
        for existing_cred in data:
            if existing_cred['strava_data']['athlete']['id'] == credentials['strava_data']['athlete']['id']:
                if credentials['vars']:
                    existing_cred['vars'] = credentials['vars']
                break
        with open(CREDENTIALS, 'w') as f:
            json.dump(data, f, default=serialize, indent=4)


def save_routes(activity: Activity, user: Athlete):
    new_route = {
        "user_id": user.user_id,
        "discord_user_id": user.discord_id,
        "user_name": user.username,
        "activity_id": activity.id,
        "type": activity.type,
        "start_date": activity.start_date,
        "moving_time": activity.duration,
        "distance": activity.distance,
        "total_elevation_gain": activity.elev_gain,
        "map": activity.map
    }

    with file_lock:
        data = {"metadata": {"total_moving_time": 0, "total_distance": 0, "total_elevation_gain": 0}, "routes": []}
        
        if os.path.exists(ROUTES) and os.path.getsize(ROUTES) > 0:
            with open(ROUTES, 'r') as file:
                data = json.load(file)
                
        existing_route_index = next((index for (index, d) in enumerate(data["routes"]) if d["activity_id"] == new_route["activity_id"]), None)
        
        if existing_route_index is not None:
            # Subtract old values from metadata
            old_route = data["routes"][existing_route_index]
            data["metadata"]["total_moving_time"] -= old_route.get("moving_time", 0)
            data["metadata"]["total_distance"] -= old_route.get("distance", 0)
            data["metadata"]["total_elevation_gain"] -= old_route.get("total_elevation_gain", 0)
            
            # Replace the existing route
            data["routes"][existing_route_index] = new_route
        else:
            # Append the new route
            data["routes"].append(new_route)
        
        # Add new values to metadata
        data["metadata"]["total_moving_time"] += new_route.get("moving_time", 0)
        data["metadata"]["total_distance"] += new_route.get("distance", 0)
        data["metadata"]["total_elevation_gain"] += new_route.get("total_elevation_gain", 0)
        
        with open(ROUTES, 'w') as f:
            json.dump(data, f, default=serialize, indent=4)



def load_or_create_credentials():
    # Create the data directory if it doesn't exist
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    # Load existing data or initialize it
    if os.path.exists(CREDENTIALS) and os.path.getsize(CREDENTIALS) > 0:
        with open(CREDENTIALS, 'r') as file:
            data = json.load(file)
    else:
        data = []

    return data


def load_credentials():
    """
    Loads user credentials from a file.

    This function checks if a file with user credentials exists, and if so, loads and returns the credentials.
    """
    with file_lock:
        if os.path.exists(CREDENTIALS) and os.path.getsize(CREDENTIALS) != 0:
            with open(CREDENTIALS, 'r') as f:
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
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj
