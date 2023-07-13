"""
file: auth_data_controller.py

description: This module handles saving and loading credentials for the Discord bot.

Author: Julian Friedl
"""

import json
import os

SRC_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.dirname(SRC_PATH)
DATA_PATH = os.path.join(os.path.dirname(BASE_PATH), 'data')
FILENAME = os.path.join(DATA_PATH, 'credentials.json')

def save_credentials(response):
    """
    Saves user credentials to a file.
    
    This function takes a JSON string containing user credentials, 
    checks if a file for the user already exists, and either appends to or overwrites the file.
    """
    json_response = json.loads(response)

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    # and keyword has short circuit behavior -> if the first condition isn't met the second one is not evaluated 
    if os.path.exists(FILENAME) and os.path.getsize(FILENAME) != 0:
        with open(FILENAME, 'r') as f:
            data = json.load(f)
            for i in range(len(data)):
                if data[i]["athlete"]["id"] == json_response["athlete"]["id"]:
                    data[i] = json_response
                    break
            else:
                data.append(json_response)     
    else:
        data = [json_response]

    with open(FILENAME, 'w') as f:
        json.dump(data, f, default=serialize, indent=4)

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
