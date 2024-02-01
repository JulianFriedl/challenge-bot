"""
week_command.py

This module contains classes and functions for handling Strava challenge data.

Author: Julian Friedl
"""

import datetime
import discord
import logging

import services.auth_data_controller as auth_data_controller
from api.api_calls import API_CALL_TYPE
from models.athlete import Athlete
from models.activity import Activity
from config.log_config import setup_logging


# Set up logging at the beginning of your script
setup_logging()

# Now you can use logging in this module
logger = logging.getLogger(__name__)


class WeekCommand:

    def __init__(self, week: int):
        """
        Initializes a WeekCommand object with the specified week.

        This method sets the week number, year, start date, and end date based on the provided week.
        """
        self.week = week
        self.year = datetime.date.today().year
        self.start_date = datetime.date.fromisocalendar(self.year, week, 1)
        # end_date is exclusive in the strava API so use the next day at 00:00:00 time
        self.end_date = datetime.date.fromisocalendar(self.year, week, 7) + datetime.timedelta(days=1)

    def get_who_needs_to_pay(self):
        """
        Returns an embed message with the athletes who need to pay for the week.

        This method retrieves the activities for each athlete and determines if they need to pay based on the points earned.
        It returns a Discord embed message with the payment details for the week.
        """
        loaded_creds = auth_data_controller.load_credentials()
        if loaded_creds is None:
            embed = discord.Embed(title="No Athletes Registered",
                                  description="There are no authenticated athletes. Please use the /strava_auth command.",
                                  color=discord.Color.red())
            return embed

        if self.end_date > datetime.date.today():
            embed = discord.Embed(title="Invalid Date",
                                  description="Error: The entered date exceeds the current date. Please enter a valid week number.",
                                  color=discord.Color.red())
            return embed

        embed = discord.Embed(
            title=f"Woche {self.week}. *({self.start_date} - {self.end_date - datetime.timedelta(days=1)})*",
            color=discord.Color.blue()
        )
        num_of_API_requests = 0
        num_of_retrieve_Cache = 0
        for cred in loaded_creds:
            athlete = Athlete(cred)
            result, error_embed, api_call_type = athlete.fetch_activities(self.start_date, self.end_date)
            if api_call_type == API_CALL_TYPE.API:
                num_of_API_requests += 1
            elif api_call_type == API_CALL_TYPE.Cache:
                num_of_retrieve_Cache += 1
            if api_call_type == API_CALL_TYPE.Error:
                return error_embed
            else:
                activities = result
            points = self.get_points(activities, athlete)
            if self.week in athlete.joker_weeks:
                embed.add_field(name=athlete.username, value=f"Muas net zoin JOKER! {points}/{athlete.points_required}  Punkt/e.🃏\n", inline=False)
            elif points < (athlete.points_required):
                embed.add_field(name=athlete.username, value=f"Muas zoin! {points}/{athlete.points_required} Punkt/e.❌\n", inline=False)
            else:
                embed.add_field(name=athlete.username, value=f"Muas net zoin! {points}/{athlete.points_required} Punkt/e.✅\n", inline=False)
        
        embed.add_field(name="Api requests", value=f"{num_of_API_requests} requests to the strava API. {num_of_retrieve_Cache} retrieved from cache.\n", inline=False)

        return embed

    # in week_command.py file, inside WeekCommand class
    def get_points(self, activities: dict, athlete: Athlete):
        """
        Calculates the total points earned for the activities within the week.

        This method iterates over the activities and calculates the points earned based on HIT workouts and activity duration.
        It returns the total points earned.
        """
        logger.info(f"Week: {self.week}")
        points = 0
        hit_counter = 0
        activities_done_set = set()
        #reverse it because strava orders the most recent one on top
        for activity_data in reversed(activities):
            activity = Activity(activity_data)
            if activity.is_in_week(self.week):
                hit_counter = activity.count_hit_workouts(hit_counter, activities_done_set, athlete)
                if hit_counter == athlete.hit_required:
                    points += 1
                    activities_done_set.add((activity.type, activity.date))
                    hit_counter = 0
                    logger.debug(
                    f"{athlete.username} Added 1 point for hit_counter: {hit_counter}\n"
                    f"Total points now: {points}\n"
                    f"Date: {activity.date}, Type: {activity.type}, Duration: {activity.duration}")
                else:
                    points_from_activity = activity.calculate_points(activities_done_set, athlete)
                    points += points_from_activity
                    logger.debug(
                    f"{athlete.username} Added {points_from_activity} point/s from activity\n"
                    f"Total points now: {points}\n"
                    f"Date: {activity.start_date}, Type: {activity.type}, Duration: {activity.duration}")
        return points
