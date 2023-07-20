"""
week_command.py

This module contains classes and functions for handling Strava challenge data.

Author: Julian Friedl
"""

import datetime
import time
import json
import discord

import services.auth_refresh as auth_refresh
import services.auth_data_controller as auth_data_controller
from utils.api_error_calls import API_CALL_TYPE
from utils.api_error_calls import api_request
from constants import RULES, SPAZI, WALKING_LIMIT, HIT_REQUIRED, HIT_MIN_TIME, MIN_DURATION_MULTI_DAY


class Athlete:
    def __init__(self, credentials):
        """
        Initializes an Athlete object with the provided credentials.

        This method refreshes the access token if need be, saves the updated credentials, and sets the username and access token.
        """
        self.credentials = auth_refresh.refresh_token(credentials)
        self.username = self.credentials["athlete"]["firstname"] + " " + self.credentials["athlete"]["lastname"]
        self.access_token = self.credentials["access_token"]
        self.img = self.credentials["athlete"]["profile_medium"]
        self.user_id = self.credentials["athlete"]["id"]
        auth_data_controller.save_credentials(json.dumps(self.credentials))

    def fetch_activities(self, start_date, end_date):
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


class Activity:
    RULES_ACTIVITY = RULES

    SPAZI = SPAZI
    WALKING_LIMIT = WALKING_LIMIT
    HIT_REQUIRED = HIT_REQUIRED
    HIT_MIN_TIME = HIT_MIN_TIME
    MIN_DURATION_MULTI_DAY = MIN_DURATION_MULTI_DAY # min duration you have to pass over midnight in order for a multiday activity to give you an extra point

    def __init__(self, activity_data):
        """
        Initializes an Activity object with the provided activity data.

        This method extracts the necessary information from the activity data and sets the corresponding attributes.
        """
        self.type = activity_data["type"]
        self.duration = activity_data["elapsed_time"] / 60
        self.date = datetime.datetime.strptime(activity_data["start_date_local"][:10], "%Y-%m-%d")
        self.start_date = datetime.datetime.strptime(activity_data["start_date_local"], "%Y-%m-%dT%H:%M:%SZ")
        self.elapsed_time = datetime.timedelta(seconds=int(activity_data["elapsed_time"]))

    def is_in_week(self, week):
        """
        Checks if the activity falls within the specified week.

        This method compares the week of the activity's date with the specified week number.
        It returns True if the activity falls within the week, otherwise False.
        """
        return self.date.isocalendar()[1] == week

    def count_hit_workouts(self, hit_counter, activities_done_set):
        """
        Counts the number of HIT workouts for the activity.

        This method checks if the activity is a HIT workout or WeighTraining and meets the duration criteria.
        If the activity is not already counted and meets the criteria, it increments the hit_counter by 1.
        It returns the updated hit_counter.
        """
        if (self.type == "Workout" or self.type == "WeightTraining") and self.HIT_MIN_TIME < self.duration < (60 - self.SPAZI):
            dates_done = {a[1] for a in activities_done_set}
            if self.date not in dates_done:
                return hit_counter + 1
            else:
                print("↓Won't add point/increased hit_counter for workout/weight-training because a point was already earned on the day.↓")
        return hit_counter

    def calculate_points(self, activities_done_set):
        """
        Calculates the points earned for the activity.

        This method checks if the activity type is valid and meets the duration criteria.
        If the activity is not already counted, it calculates the points based on the activity type and duration.
        It returns the calculated points.
        """
        points = 0
        if self.type in self.RULES_ACTIVITY and self.duration >= self.RULES_ACTIVITY[self.type] - self.SPAZI:
            walk_count = len([a for a in activities_done_set if a[0] == "Walk"])
            if walk_count >= self.WALKING_LIMIT and self.type == "Walk":
                print(f"Did not add point for Walk because walk_count >= WALKING_LIMIT date: {self.date} type: {self.type}")
                return points
            dates_done = {a[1] for a in activities_done_set}
            if self.date not in dates_done:
                end_date = self.start_date + self.elapsed_time
                start_ordinal = self.start_date.toordinal()
                end_ordinal = end_date.toordinal()
                days = end_ordinal - start_ordinal + 1
                elapsed_time_past_midnight_min = end_date.hour * 60 + end_date.minute

                if days > 1 and elapsed_time_past_midnight_min < self.MIN_DURATION_MULTI_DAY:
                    print(f"Didn't add {days} points because elapsed_time_past_midnight_min: {elapsed_time_past_midnight_min} which is under the threshold date: {self.start_date} type: {self.type}")
                    days -= 1

                points += days
                activities_done_set.add((self.type, self.date))
        return points


class WeekCommand:
    POINTS_REQUIRED = 3

    def __init__(self, week):
        """
        Initializes a WeekCommand object with the specified week.

        This method sets the week number, year, start date, and end date based on the provided week.
        """
        self.week = week
        self.year = datetime.date.today().year
        self.start_date = datetime.date.fromisocalendar(self.year, week, 1)
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
                                  description="There are no authenticated athletes. Please use the !strava_auth command.",
                                  color=discord.Color.red())
            return embed

        if self.end_date > datetime.date.today():
            embed = discord.Embed(title="Invalid Date",
                                  description="Error: The entered date exceeds the current date. Please enter a valid week number.",
                                  color=discord.Color.red())
            return embed

        embed = discord.Embed(
            title=f"Woche {self.week}. *({self.start_date} - {self.end_date})*",
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
            points = self.get_points(activities, athlete.username)
            if points < (self.POINTS_REQUIRED if self.week >= 9 else 2):
                embed.add_field(name=athlete.username, value=f"Muas zoin! {points} Punkt/e.❌\n", inline=False)
            else:
                embed.add_field(name=athlete.username, value=f"Muas net zoin! {points} Punkt/e.✅\n", inline=False)
        
        embed.add_field(name="Api requests", value=f"{num_of_API_requests} requests to the strava API. {num_of_retrieve_Cache} retrieved from cache.\n", inline=False)

        return embed

    # in week_command.py file, inside WeekCommand class
    def get_points(self, activities, username):
        """
        Calculates the total points earned for the activities within the week.

        This method iterates over the activities and calculates the points earned based on HIT workouts and activity duration.
        It returns the total points earned.
        """
        print(f"Week: {self.week}")
        points = 0
        hit_counter = 0
        activities_done_set = set()
        #reverse it because strava orders the most recent one on top
        for activity_data in reversed(activities):
            activity = Activity(activity_data)
            if activity.is_in_week(self.week):
                hit_counter = activity.count_hit_workouts(hit_counter, activities_done_set)
                if hit_counter == Activity.HIT_REQUIRED:
                    points += 1
                    activities_done_set.add((activity.type, activity.date))
                    hit_counter = 0
                    print(f"{username} Added 1 point for hit_counter being equal to HIT_REQUIRED, total points now: {points} Date: {activity.date} Type: {activity.type}")
                else:
                    points_from_activity = activity.calculate_points(activities_done_set)
                    points += points_from_activity
                    print(f"{username} Added {points_from_activity} point/s from activity, total points now: {points} Date: {activity.start_date} Type: {activity.type}")
        return points
