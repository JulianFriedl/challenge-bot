"""
file: routes_data_controller.py

description: This module handles saving and loading routes.

Author: Julian Friedl
"""

import datetime
import json
import os
from dotenv import load_dotenv
import logging
import polyline
from geopy.distance import geodesic

from src.shared.config.log_config import setup_logging
from threading import Lock

from src.shared.models.activity import Activity
from src.shared.models.athlete import Athlete

file_lock = Lock()  # locking mechanism for threading

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

YEAR = int(os.getenv("YEAR", datetime.date.today().year))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
YEAR_PATH = os.path.join(DATA_PATH, str(YEAR))
ROUTES = os.path.join(YEAR_PATH, 'routes.json')


def save_routes(activity:Activity, user:Athlete):
    # Construct the URL for the activity
    activity_url = f"https://www.strava.com/activities/{activity.id}"
    
    new_route = {
        "activity_id": activity.id,
        "name": activity.name,
        "type": activity.type,
        "start_date": activity.start_date,
        "moving_time": activity.duration,
        "distance": activity.distance,
        "total_elevation_gain": activity.elev_gain,
        "map": activity.map,
        "kudos": activity.kudos,
        "suffer_score": activity.suffer_score,
        "url": activity_url
    }

    if new_route["map"]["summary_polyline"] == "":
        return
    
    if new_route["type"] == "VirtualRide":
        return

    with file_lock:
        if os.path.exists(ROUTES) and os.path.getsize(ROUTES) > 0:
            with open(ROUTES, 'r') as file:
                data = json.load(file)
        else:
            data = {"metadata": {"total_moving_time": 0, "total_distance": 0, "total_elevation_gain": 0}, "athletes": {}}

        # Ensure athlete structure exists
        athlete_data = data["athletes"].setdefault(str(user.user_id), {
            "user_id": user.user_id,
            "discord_user_id": user.discord_id,
            "user_name": user.username,
            "metadata": {"total_moving_time": 0, "total_distance": 0, "total_elevation_gain": 0},
            "routes": []
        })

        # Check for existing route to replace
        existing_route = next((route for route in athlete_data["routes"] if route["activity_id"] == new_route["activity_id"]), None)

        if existing_route:
            for metric, meta_key in [("moving_time", "total_moving_time"), ("distance", "total_distance"), ("total_elevation_gain", "total_elevation_gain")]:
                data["metadata"][meta_key] -= existing_route.get(metric, 0)
                athlete_data["metadata"][meta_key] -= existing_route.get(metric, 0)

        # Correctly mapping new_route's keys to metadata keys when adding
        for metric, meta_key in [("moving_time", "total_moving_time"), ("distance", "total_distance"), ("total_elevation_gain", "total_elevation_gain")]:
            value = new_route.get(metric, 0)
            data["metadata"][meta_key] += value
            athlete_data["metadata"][meta_key] += value


        # Append the new or updated route
        athlete_data["routes"].append(new_route)

        with open(ROUTES, 'w') as f:
            json.dump(data, f, default=serialize, indent=4)

def load_routes(years:str):
    all_data = {}
    for year in years.split(','):
        YEAR_PATH = os.path.join(DATA_PATH, str(year))
        ROUTES = os.path.join(YEAR_PATH, 'routes.json')
        if os.path.exists(ROUTES) and os.path.getsize(ROUTES) > 0:
            with open(ROUTES) as file:
                data = json.load(file)
            all_data[str(year)] = data
        else:
            all_data[str(year)] = {}  
    return all_data

def available_years():
    years = [name for name in os.listdir(DATA_PATH) 
                if os.path.isdir(os.path.join(DATA_PATH, name)) 
                and name.isdigit()]  # Ensure directory names are digits
    return sorted(years)  # Return sorted list of years

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
