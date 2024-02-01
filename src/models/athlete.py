"""
athlete.py

This module contains the model for athletes.

Author: Julian Friedl
"""

import datetime
import time
import json


import services.auth_refresh as auth_refresh
import services.auth_data_controller as auth_data_controller
from api.api_calls import api_request


class Athlete:
    def __init__(self, credentials: dict):
        """
        Initializes an Athlete object with the provided credentials.

        This method refreshes the access token if need be, saves the updated credentials, and sets the username and access token.
        """
        self.credentials = auth_refresh.refresh_token(credentials)
        self.username = self.credentials['strava_data']["athlete"]["firstname"] + " " + self.credentials['strava_data']["athlete"]["lastname"]
        self.access_token = self.credentials['strava_data']["access_token"]
        self.img = self.credentials['strava_data']["athlete"]["profile_medium"]
        self.user_id = self.credentials['strava_data']["athlete"]["id"]

        # Extracting additional data from credentials
        self.rules = self.credentials.get('constants', {}).get('rules', {})
        self.points_required = self.credentials.get('constants', {}).get('points_required')
        self.price_per_week = self.credentials.get('constants', {}).get('price_per_week')
        self.spazi = self.credentials.get('constants', {}).get('spazi', 0)
        self.walking_limit = self.credentials.get('constants', {}).get('walking_limit', 0)
        self.hit_required = self.credentials.get('constants', {}).get('hit_required', 0)
        self.hit_min_time = self.credentials.get('constants', {}).get('hit_min_time', 0)
        self.min_duration_multi_day = self.credentials.get('constants', {}).get('min_duration_multi_day', 0)
        
        self.joker = self.credentials.get('vars', {}).get('joker', 0)
        self.joker_weeks = self.credentials.get('vars', {}).get('joker_weeks', [])

        self.discord_id = self.credentials.get('discord_id', 0)

        auth_data_controller.save_strava_credentials(json.dumps(self.credentials))

    def fetch_activities(self, start_date : datetime, end_date : datetime):
        """
        Fetches the activities for the athlete within the specified date range.

        This method makes an API call to retrieve the activities for the athlete within the specified date range.
        It returns a tuple with the JSON response if the API call is successful, and an error embed if an error occurred.
        """
        start_date_seconds = time.mktime(start_date.timetuple())
        end_date_seconds = time.mktime(end_date.timetuple())
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"before": end_date_seconds, "after": start_date_seconds}
        response, error_embed, api_call_type  = api_request("https://www.strava.com/api/v3/athlete/activities", headers, params, self.username, self.user_id)
        return (response, error_embed, api_call_type)
