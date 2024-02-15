"""
week_command.py

This module contains classes and functions for handling Strava challenge data.

Author: Julian Friedl
"""

import datetime
import discord
import logging
import os
from dotenv import load_dotenv

import src.shared.services.athlete_data_controller as athlete_data_controller
import src.shared.services.routes_data_controller as routes_data_controller
from src.shared.models.athlete import Athlete
from src.shared.models.activity import Activity
from src.shared.config.log_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

YEAR = int(os.getenv("YEAR", datetime.date.today().year))

RULES = athlete_data_controller.load_global_rules()

MULTIPLIER = RULES["MULTIPLIER"]
MULTIPLIER_ON = RULES["MULTIPLIER_ON"]

class WeekCommand:

    def __init__(self, week: int):
        """
        Initializes a WeekCommand object with the specified week.

        This method sets the week number, year, start date, and end date based on the provided week.
        """
        self.week = week
        self.year = YEAR  # Use YEAR from the environment variable or the current year if not set
        if self.year == datetime.date.today().year:
            # For the current year, check if the week is not beyond the current week
            current_week = datetime.date.today().isocalendar()[1]
            if week > current_week:
                raise ValueError("Week number cannot be in the future for the current year")
        self.start_date = datetime.date.fromisocalendar(self.year, week, 1)
        # end_date is exclusive in the Strava API so use the next day at 00:00:00 time
        self.end_date = datetime.date.fromisocalendar(self.year, week, 7) + datetime.timedelta(days=1)
        self.num_of_API_requests = 0
        self.num_of_retrieve_Cache = 0

    def excecute_week_command(self):
        """
        Returns an embed message with the athletes who need to pay for the week.

        This method retrieves the activities for each athlete and determines if they need to pay based on the points earned.
        It returns a Discord embed message with the payment details for the week.
        """
        logger.info(f"Week Command called, week:{self.week}.")
        loaded_creds = athlete_data_controller.load_athletes()
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

        # Initialize a list to hold athlete data and points
        athlete_data = []

        # Collect data and points for each athlete
        for cred in loaded_creds:
            athlete = Athlete(cred)
            activities, num_of_API_requests, num_of_retrieve_Cache = athlete.fetch_athlete_activities(self.start_date, self.end_date)
            points = self.get_points(activities, athlete)
            self.num_of_API_requests += num_of_API_requests
            self.num_of_retrieve_Cache += num_of_retrieve_Cache

            # Calculate the amount if required
            amount = athlete.price_per_week * self.get_price_multiplier(athlete) if points < athlete.points_required else 0

            # Append athlete data including calculated amount or flag for Joker status
            athlete_data.append((athlete.username, points, athlete.points_required, amount, self.week in athlete.joker_weeks))

        # Sort the list by points in descending order
        sorted_athlete_data = sorted(athlete_data, key=lambda x: x[1], reverse=True)

        # Initialize variables to track previous points and adjusted placement
        previous_points = None
        adjusted_placement = 0
        actual_placement = 0  # This counts the actual number of iterations

        # Loop through the sorted list to add fields to the embed, handling ties
        for username, points, points_required, amount, is_joker in sorted_athlete_data:
            actual_placement += 1
            # Check if the current points are different from the previous points to adjust placement for ties
            if points != previous_points:
                adjusted_placement = actual_placement
            previous_points = points

            # Determine placement and assign corresponding emoji based on adjusted placement
            placement_emoji = ""
            if adjusted_placement == 1:  # First place
                placement_emoji = "🥇"
            # elif adjusted_placement == 2:  # Second place
            #     placement_emoji = "🥈"
            # elif adjusted_placement == 3:  # Third place
            #     placement_emoji = "🥉"
            
            # Construct the value string based on athlete's status
            if is_joker:
                value = f"{placement_emoji}muas net zoin JOKER! {points}/{points_required} Punkt/e.🃏\n"
            elif points < points_required:
                value = f"{placement_emoji}muas {amount}€ zoin! {points}/{points_required} Punkt/e.❌\n"
            else:
                value = f"{placement_emoji}muas net zoin! {points}/{points_required} Punkt/e.✅\n"
            
            # Add the field to the embed with the athlete's information
            embed.add_field(name=username, value=value, inline=False)

        # Add API request information
        embed.add_field(name="Api requests", value=f"{self.num_of_API_requests} requests to the strava API. {self.num_of_retrieve_Cache} retrieved from cache.\n", inline=False)

        return embed

    # in week_command.py file, inside WeekCommand class
    def get_points(self, activities: dict, athlete: Athlete):
        """
        Calculates the total points earned for the activities within the week.

        This method iterates over the activities and calculates the points earned based on HIT workouts and activity duration.
        It returns the total points earned.
        """
        
        points = 0
        hit_counter = 0
        activities_done_set = set()
        # reverse it because strava orders the most recent one on top
        for activity_data in reversed(activities):
            activity = Activity(activity_data)
            if activity.is_in_week(self.week):
                routes_data_controller.save_routes(activity, athlete) # save the map data for later usage
                hit_counter = activity.count_hit_workouts(
                    hit_counter, activities_done_set, athlete)
                if hit_counter == athlete.hit_required:
                    points += 1
                    activities_done_set.add((activity.type, activity.date))
                    hit_counter = 0
                    logger.debug(
                        f"{athlete.username} Added 1 point for hit_counter: {hit_counter}\n"
                        f"Total points now: {points}\n"
                        f"Date: {activity.date}, Type: {activity.type}, Duration: {activity.duration}")
                else:
                    points_from_activity = activity.calculate_points(
                        activities_done_set, athlete)
                    points += points_from_activity
                    logger.debug(
                        f"{athlete.username} Added {points_from_activity} point/s from activity\n"
                        f"Total points now: {points}\n"
                        f"Date: {activity.start_date}, Type: {activity.type}, Duration: {activity.duration}")
        
        # Insert week into week_results
        existing_weeks = set(int(week_result.split("_")[0]) for week_result in athlete.week_results)

        if self.week not in existing_weeks:
            # Week does not exist, insert new result
            insert_pos = self.week - 1  # Assuming week numbers are 1-based and list is 0-based
            if self.week in athlete.joker_weeks:
                athlete.week_results.insert(insert_pos, f"{self.week}_2")
            elif points < athlete.points_required:
                athlete.week_results.insert(insert_pos, f"{self.week}_0")
            else:
                athlete.week_results.insert(insert_pos, f"{self.week}_1")
        else:
            # Week exists, replace the result
            for i, week_result in enumerate(athlete.week_results):
                week_num = int(week_result.split("_")[0])
                if week_num == self.week:
                    if self.week in athlete.joker_weeks:
                        athlete.week_results[i] = f"{self.week}_2"
                    elif points < athlete.points_required:
                        athlete.week_results[i] = f"{self.week}_0"
                    else:
                        athlete.week_results[i] = f"{self.week}_1"
                    break  # Exit the loop once the week is found and updated

        # Update athlete credentials with the new week results
        athlete.credentials["vars"]["week_results"] = athlete.week_results

        # Call the function to update the athlete's vars in storage or database
        athlete_data_controller.update_athlete_vars(athlete.credentials)

        return points

    def get_price_multiplier(self, athlete: Athlete):
        """
        Calculates the price multiplier for an athlete based on the number of weeks missed.
    
        Parameters:
        - athlete (Athlete): The athlete object containing week results and other relevant data.

        Returns:
        - float: The calculated multiplier, which is a constant MULTIPLIER raised to the power of missed weeks count.
        """
        if not MULTIPLIER_ON:
            return 1
        
        self.get_missing_weeks(athlete)#get any weeks that are missing for the calculation
        missed_weeks_count = 0
        for week_result in reversed(athlete.week_results):
            week = int(week_result.split("_")[0])
            result = int(week_result.split("_")[1])
            if week >= self.week:
                continue
            if result == 1:
                break
            elif result == 0:
                missed_weeks_count += 1
            elif result == 2:  # joker
                continue
        
        return MULTIPLIER**(missed_weeks_count)

    def get_missing_weeks(self, athlete: Athlete):
        """
        Identifies missing weeks in an athlete's performance records up to the current week and makes an API request
        to fetch activities for those weeks if any are missing.

        Parameters:
        - athlete (Athlete): The athlete object whose week results are to be analyzed.

        Returns:
        - None: This function does not return a value but updates the athlete's records with fetched activities for missing weeks.
        """
        
        # check if past weeks data is complete for the price multiplier calculation
        weeks_missing = []
        week_number = self.week

        # Parse the week results into a dictionary {week: result}
        week_results_dict = {int(result.split("_")[0]): int(result.split("_")[1]) for result in athlete.week_results}

        # If all results are 1 or there are no results, no missing weeks are considered
        if week_results_dict.get(self.week-1) == 1:
            return

        # Iterate through all weeks from 1 to the current week
        for week in reversed(range(1, week_number + 1)):
            if week not in week_results_dict.keys():
                weeks_missing.append(week)
        if weeks_missing != []:
            self.missing_weeks_api_request(weeks_missing, athlete)

    def missing_weeks_api_request(self, weeks_missing: list, athlete: Athlete):
        """
        Performs an API request to retrieve activities for a range of missing weeks for the given athlete.

        Parameters:
        - weeks_missing (list): A list of integers representing the missing weeks for which activities need to be fetched.
        - athlete (Athlete): The athlete object for whom activities are being fetched.

        Returns:
        - None: This function does not return a value but updates the athlete's records with the fetched activities.
        """
        start_date = datetime.date.fromisocalendar(self.year, weeks_missing[len(weeks_missing)-1], 1)
        # end_date is exclusive in the strava API so use the next day at 00:00:00 time
        end_date = datetime.date.fromisocalendar(
            self.year, weeks_missing[0], 7) + datetime.timedelta(days=1)
        activities, num_of_API_requests, num_of_retrieve_Cache  = athlete.fetch_athlete_activities(start_date, end_date, cache=False)
        self.num_of_API_requests += num_of_API_requests
        self.num_of_retrieve_Cache += num_of_retrieve_Cache

        for week in range(weeks_missing[len(weeks_missing)-1], weeks_missing[0]+1): # plus 1 because in range isn't inclusive
            WeekCommand(week).get_points(activities, athlete)