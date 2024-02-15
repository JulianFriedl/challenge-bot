"""
athlete.py

This module contains the model for athletes.

Author: Julian Friedl
"""

import datetime
import time
import json
import logging


import src.shared.services.auth_refresh as auth_refresh
import src.shared.services.athlete_data_controller as athlete_data_controller
from src.shared.api.api_calls import api_request, API_CALL_TYPE
from src.shared.config.log_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

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
        self.week_results = self.credentials.get('vars', {}).get('week_results', [])

        self.discord_id = self.credentials.get('discord_user_id', 0)

        athlete_data_controller.save_strava_athletes(json.dumps(self.credentials))

    def fetch_athlete_activities(self, start_date : datetime, end_date : datetime, cache:bool = True):
        """
        Fetch all the activities in a year. The api can send a max of 200 Activities per request. 
        By iterating over the page parameter until I either get an error or the returned data is null,
        I get all the activities and append them to a list.

        Returns:
        activities (list of activities)
        error_embed (discord.Embed or None): None if the request was successful, otherwise a Discord embed with the error message.
        
        """
        start_date_seconds = time.mktime(start_date.timetuple())
        end_date_seconds = time.mktime(end_date.timetuple())
        activities = []
        page = 1
        PER_PAGE = 200
        per_page = PER_PAGE
        end_of_results = False

        num_of_API_requests = 0
        num_of_retrieve_Cache = 0
        while not end_of_results:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {"before": end_date_seconds, "after": start_date_seconds, "page": page, "per_page": per_page}
            
            data, api_call_type = api_request("https://www.strava.com/api/v3/athlete/activities", headers, params, self.username, self.user_id, cache=cache)
            if api_call_type == API_CALL_TYPE.API:
                num_of_API_requests += 1
            elif api_call_type == API_CALL_TYPE.Cache:
                num_of_retrieve_Cache += 1
            if not data:
                end_of_results = True
            else:
                activities.extend(data)

                page += 1
            
            #check if the response is smaller than the Per_page limit, meaning that all results were retrieved
            if len(activities) < PER_PAGE:
                end_of_results = True
        return (activities, num_of_API_requests, num_of_retrieve_Cache)
       