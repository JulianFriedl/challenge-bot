"""
activity.py

This module contains the model for activites.

Author: Julian Friedl
"""

import datetime
import logging

from src.shared.models.athlete import Athlete
from src.shared.config.log_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class Activity:

    def __init__(self, activity_data: dict):
        """
        Initializes an Activity object with the provided activity data.

        This method extracts the necessary information from the activity data and sets the corresponding attributes.
        """
        self.id = activity_data.get("id")
        self.type = activity_data.get("type")
        self.duration = activity_data.get("moving_time", 0) / 60  
        self.date = datetime.datetime.strptime(activity_data.get("start_date_local", "1900-01-01")[:10], "%Y-%m-%d")
            
        # Handling start_date with a default date if not present
        start_date_local = activity_data.get("start_date_local", "1900-01-01T00:00:00Z")
        self.start_date = datetime.datetime.strptime(start_date_local, "%Y-%m-%dT%H:%M:%SZ")
        self.elapsed_time = datetime.timedelta(seconds=int(activity_data.get("elapsed_time", 0)))
            
        # For routes
        self.name = activity_data.get("name", "")
        self.suffer_score = self.suffer_score = activity_data.get("suffer_score", 0)
        self.kudos = activity_data.get("kudos_count", 0) 
        self.map = activity_data.get("map", {})  
        self.distance = activity_data.get("distance", 0) / 1000  
        self.elev_gain = activity_data.get("total_elevation_gain", 0) 

    def is_in_week(self, week : int):
        """
        Checks if the activity falls within the specified week.

        This method compares the week of the activity's date with the specified week number.
        It returns True if the activity falls within the week, otherwise False.
        """
        return self.date.isocalendar()[1] == week

    def count_hit_workouts(self, hit_counter: int, activities_done_set: set, athlete: Athlete):
        """
        Counts the number of HIT workouts for the activity.

        This method checks if the activity is a HIT workout or WeighTraining and meets the duration criteria.
        If the activity is not already counted and meets the criteria, it increments the hit_counter by 1.
        It returns the updated hit_counter.
        """
        if (self.type == "Workout" or self.type == "WeightTraining") and athlete.hit_min_time < self.duration < (60 - athlete.spazi):
            dates_done = {a[1] for a in activities_done_set}
            if self.date not in dates_done:
                return hit_counter + 1
            else:
                logger.debug("Won't add point/increased hit_counter for workout/weight-training because a point was already earned on the day.")

        return hit_counter

    def calculate_points(self, activities_done_set: set, athlete: Athlete):
        """
        Calculates the points earned for the activity.

        This method checks if the activity type is valid and meets the duration criteria.
        If the activity is not already counted, it calculates the points based on the activity type and duration.
        It returns the calculated points.
        """
        points = 0
        if self.type in athlete.rules and self.duration >= athlete.rules[self.type] - athlete.spazi:
            walk_count = len([a for a in activities_done_set if a[0] == "Walk"])
            if walk_count >= athlete.walking_limit and self.type == "Walk":
                logger.debug(
                f"Skipped adding point for Walk. Reason: walk_count >= WALKING_LIMIT\n"
                f"Date: {self.start_date}, Type: {self.type}")
                return points
            dates_done = {a[1] for a in activities_done_set}
            if self.date not in dates_done:
                end_date = self.start_date + self.elapsed_time
                start_ordinal = self.start_date.toordinal()
                end_ordinal = end_date.toordinal()
                days = end_ordinal - start_ordinal + 1
                elapsed_time_past_midnight_min = end_date.hour * 60 + end_date.minute

                if days > 1 and elapsed_time_past_midnight_min < athlete.min_duration_multi_day:
                    logger.debug(
                    f"Skipped adding {days} points for multi-day activity.\n"
                    f"Reason: elapsed_time_past_midnight_min ({elapsed_time_past_midnight_min}) is under the threshold\n"
                    f"Date: {self.start_date}, Type: {self.type}")
                    days -= 1

                points += days
                activities_done_set.add((self.type, self.date))
        return points

