"""
total_command.py

This module contains classes and functions for handling the total command.

Author: Julian Friedl
"""

import datetime
import time
import discord
import logging

import services.auth_data_controller as auth_data_controller
from commands.week_command import WeekCommand
from api.api_calls import API_CALL_TYPE
from models.athlete import Athlete
from config.rules_preset import CHALLENGE_START_WEEK, MULTIPLIER, MULTIPLIER_ON
from config.log_config import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

class TotalCommand:
    num_of_API_requests = 0
    num_of_retrieve_Cache = 0

    
    def get_yearly_payments(self):
        """
        Check yearly payments for each athlete and return a message indicating
        whether they need to pay or not for the current year. 
        """
        logger.info(f"Total Command Called.")
        current_date = datetime.date.today()
        current_year = current_date.year
        current_week = datetime.date.today().isocalendar()[1]
        week_before_current_week = current_week - 1

        # get the start and end date by taking the first day in the challenge start week, and the last day of the week before the current week
        start_date = datetime.date.fromisocalendar(current_year, CHALLENGE_START_WEEK, 1)
        # end_date is exclusive in the Strava API so use the next day at 00:00:00 time
        end_date = datetime.date.fromisocalendar(current_year, week_before_current_week, 7) + datetime.timedelta(days=1)

        loaded_creds = auth_data_controller.load_credentials()

        if loaded_creds is None:
            embed = discord.Embed(title="No Athletes Registered",
                                  description="There are no authenticated athletes. Please use the /strava_auth command.",
                                  color=discord.Color.red())
            return embed

        amounts = {}

        for cred in loaded_creds:
            athlete = Athlete(cred)
            activities, self.num_of_API_requests, self.num_of_retrieve_Cache = athlete.fetch_athlete_activities(start_date, end_date)

            amount_to_pay = 0
            price_multiplier = 0 #used for tracking how much the price has to be multiplied based on missed weeks
            for week in range(CHALLENGE_START_WEEK, week_before_current_week+1): # plus 1 because in range isn't inclusive
                points_in_week = WeekCommand(week).get_points(activities, athlete)
                if week in athlete.joker_weeks:
                    continue
                elif points_in_week < (athlete.points_required):
                    logger.info(
                    f"{athlete.username} has to pay in week {week}. "
                    f"Reason: Only earned {points_in_week}/{athlete.points_required} points.")
                    if MULTIPLIER_ON:
                        amount_to_pay += athlete.price_per_week * MULTIPLIER**price_multiplier
                    else:
                        amount_to_pay += athlete.price_per_week
                    price_multiplier+=1
                else:
                    price_multiplier = 0
            amounts[athlete.username] = amount_to_pay

        return self.create_payment_embed(amounts, current_year)


    def create_payment_embed(self, amounts: dict, year: int):
        """
        Create a Discord Embed object based on the payment details of each athlete in the current year.
        """
        embed = discord.Embed(
            title = f"Payment Details for {year}",
            description = "Yearly payment summary for all athletes.",
            color = discord.Color.blue()
        )

      
        # Find the maximum amount
        max_amount = max(amounts.values())

        # Loop through the amounts and add fields to the embed
        for username, amount in amounts.items():
            if amount > 0:
                # Check if the amount is the max amount and add a special emoji
                emoji = "🤑" if amount == max_amount else ""
                embed.add_field(name=username, value=f"muas {amount}€ zoin.{emoji}", inline=False)
            else:
                embed.add_field(name=username, value=f"muas nix zoin.", inline=False)
        embed.add_field(name="Api requests", value=f"{self.num_of_API_requests} requests to the strava API. {self.num_of_retrieve_Cache} retrieved from cache.\n", inline=False)


        return embed
