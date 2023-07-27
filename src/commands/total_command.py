"""
total_command.py

This module contains classes and functions for handling the total command.

Author: Julian Friedl
"""

import datetime
import time
import requests
import json
import discord

import services.auth_refresh as auth_refresh
import services.auth_data_controller as auth_data_controller
import commands.week_command as week_command
from utils.api_error_calls import api_request
from utils.api_error_calls import API_CALL_TYPE
from constants import CHALLENGE_START_WEEK, PRICE_PER_WEEK

class TotalCommand:
    num_of_API_requests = 0
    num_of_retrieve_Cache = 0

    
    def get_yearly_payments(self):
        """
        Check yearly payments for each athlete and return a message indicating
        whether they need to pay or not for the current year. 
        """
        current_date = datetime.date.today()
        current_year = current_date.year
        current_week = datetime.date.today().isocalendar()[1]
        week_before_current_week = current_week - 1

        # get the start and end date by taking the first day in the challenge start week, and the last day of the week before the current week
        start_date = datetime.date.fromisocalendar(current_year, CHALLENGE_START_WEEK, 1)
        # end_date is exclusive in the Strava API so use the next day at 00:00:00 time
        end_date = datetime.date.fromisocalendar(current_year, week_before_current_week, 7) + datetime.timedelta(days=1)

        start_date_seconds = time.mktime(start_date.timetuple())
        end_date_seconds = time.mktime(end_date.timetuple())

        loaded_creds = auth_data_controller.load_credentials()

        if loaded_creds is None:
            embed = discord.Embed(title="No Athletes Registered",
                                  description="There are no authenticated athletes. Please use the !strava_auth command.",
                                  color=discord.Color.red())
            return embed

        amounts = {}

        for cred in loaded_creds:
            cred = auth_refresh.refresh_token(cred)
            auth_data_controller.save_credentials(json.dumps(cred))
            username = cred["athlete"]["firstname"] + " " + cred["athlete"]["lastname"]
            user_id = cred["athlete"]["id"]
            access_token = cred["access_token"]

            activities, error_embed = self.fetch_athlete_activities(username, user_id, access_token, start_date_seconds, end_date_seconds, end_date)

            if error_embed is not None:
                return error_embed

            amount_to_pay = 0

            for week in range(CHALLENGE_START_WEEK, week_before_current_week+1): # plus 1 because in range isn't inclusive
                points_in_week = week_command.WeekCommand(week).get_points(activities, username)
                if points_in_week < (week_command.WeekCommand.POINTS_REQUIRED if week >= 9 else 2):
                    print(f"{username} has to pay in week {week} because they only earned {points_in_week} points.")
                    amount_to_pay += PRICE_PER_WEEK

            amounts[username] = amount_to_pay

        return self.create_payment_embed(amounts, current_year)


    def fetch_athlete_activities(self, username, user_id, access_token, start_date_seconds, end_date_seconds, end_date):
        """
        Fetch all the activities in a year. The api can send a max of 30 Activities per request. 
        By iterating over the page parameter until I either get an error or the returned data is null,
        I get all the activities and append them to a list.

        Returns:
        activities (list of activities)
        error_embed (discord.Embed or None): None if the request was successful, otherwise a Discord embed with the error message.
        """
        activities = []
        page = 1
        PER_PAGE = 200
        per_page = PER_PAGE
        end_of_results = False

        while not end_of_results:
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {"before": end_date_seconds, "after": start_date_seconds, "page": page, "per_page": per_page}

            data, error_embed, api_call_type = api_request("https://www.strava.com/api/v3/athlete/activities", headers, params, username, user_id)
            if api_call_type == API_CALL_TYPE.API:
                self.num_of_API_requests += 1
            elif api_call_type == API_CALL_TYPE.Cache:
                self.num_of_retrieve_Cache += 1


            if error_embed is not None:
                return activities, error_embed

            if not data:
                end_of_results = True
            else:
                activities.extend(data)

                page += 1
            
            #check if the response is smaller than the Per_page limit, meaning that all results were retrieved
            if len(activities) < PER_PAGE:
                end_of_results = True
        return activities, None

    def create_payment_embed(self, amounts: dict, year: int):
        """
        Create a Discord Embed object based on the payment details of each athlete in the current year.
        """
        embed = discord.Embed(
            title = f"Payment Details for {year}",
            description = "Yearly payment summary for all athletes.",
            color = discord.Color.blue()
        )

      
        # Find the user with the highest amount
        max_user = max(amounts, key=amounts.get)
        # Loop through the amounts and add fields to the embed
        for username, amount in amounts.items():
            if amount > 0:
                # Check if the user is the max user and add a special emoji
                emoji = "🤑" if username == max_user else ""
                embed.add_field(name=username, value=f"muas {amount} euro für {year} zahlen.{emoji}", inline=False)
            else:
                embed.add_field(name=username, value=f"muas nix für {year} zahlen.💩", inline=False)
        embed.add_field(name="Api requests", value=f"{self.num_of_API_requests} requests to the strava API. {self.num_of_retrieve_Cache} retrieved from cache.\n", inline=False)


        return embed
