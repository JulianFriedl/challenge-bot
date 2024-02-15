"""
total_command.py

This module contains classes and functions for handling the total command.

Author: Julian Friedl
"""

import datetime
import discord
import logging
import os
from dotenv import load_dotenv

import src.shared.services.athlete_data_controller as athlete_data_controller
from src.bot.commands.week_command import WeekCommand
from src.shared.models.athlete import Athlete
from src.shared.config.log_config import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

YEAR = int(os.getenv("YEAR", datetime.date.today().year))

RULES = athlete_data_controller.load_global_rules()

CHALLENGE_START_WEEK = RULES["CHALLENGE_START_WEEK"]
MULTIPLIER = RULES["MULTIPLIER"]
MULTIPLIER_ON = RULES["MULTIPLIER_ON"]

class TotalCommand:
    num_of_API_requests = 0
    num_of_retrieve_Cache = 0

    
    def get_yearly_payments(self):
        """
        Check yearly payments for each athlete and return a message indicating
        whether they need to pay or not for the current year. 
        """
        logger.info("Total Command Called.")
        current_date = datetime.date.today()
        current_year = current_date.year
        current_week = current_date.isocalendar()[1]

        if YEAR == current_year:
            # Ensure week_before_current_week is at least 1
            week_before_current_week = max(current_week - 1, 1)
        else:
            # For a past year, calculate the last week of the year
            # Ensure that the calculation does not result in week 0
            last_day_of_year = datetime.date(YEAR, 12, 31)
            week_before_current_week = last_day_of_year.isocalendar()[1]
            if week_before_current_week == 0:
                # Fallback or corrective action if needed
                week_before_current_week = 52  # A safe assumption for most years

        start_date = datetime.date.fromisocalendar(YEAR, 1, 1)  # Always start from the first week
        end_date = datetime.date.fromisocalendar(YEAR, week_before_current_week, 7) + datetime.timedelta(days=1)

        loaded_creds = athlete_data_controller.load_athletes()

        if loaded_creds is None:
            embed = discord.Embed(title="No Athletes Registered",
                                  description="There are no authenticated athletes. Please use the /strava_auth command.",
                                  color=discord.Color.red())
            return embed

        amounts = {}

        for cred in loaded_creds:
            athlete = Athlete(cred)
            
            # Parse week_results into a dictionary for easier access
            week_results_dict = {int(w.split('_')[0]): int(w.split('_')[1]) for w in athlete.week_results}

            # Determine the range of weeks to potentially fetch
            weeks_to_fetch = [week for week in range(CHALLENGE_START_WEEK, week_before_current_week + 1)
                            if week not in week_results_dict]
            
            
            if weeks_to_fetch:  # Check if the list is not empty
                start_date = datetime.date.fromisocalendar(YEAR, weeks_to_fetch[0], 1)
                # Fetch activities for the needed weeks 
                activities, api_requests, chache_retrieves = athlete.fetch_athlete_activities(start_date, end_date, cache=True)
            self.num_of_API_requests += len(weeks_to_fetch)
            self.num_of_retrieve_Cache += len(week_results_dict)
            
            amount_to_pay = 0
            price_multiplier = 0  # Used for tracking how much the price has to be multiplied based on missed weeks
            
            for week in range(CHALLENGE_START_WEEK, week_before_current_week + 1):
                result = week_results_dict.get(week, None)
                if result == 2:  # Joker week, skip payment calculation
                    continue
                elif result == 1:  # Passed week, reset multiplier
                    price_multiplier = 0
                    continue
                elif result == 0:
                    if MULTIPLIER_ON:
                        amount_to_pay += athlete.price_per_week * (MULTIPLIER ** price_multiplier)
                    else:
                        amount_to_pay += athlete.price_per_week
                    price_multiplier += 1
                
                # If week is not in week_results_dict, calculate payment
                if result is None:
                    points_in_week = WeekCommand(week).get_points(activities, athlete)
                    # Assuming get_points method or similar logic determines the result for the week
                    
                    if points_in_week < athlete.points_required:
                        logger.info(f"{athlete.username} has to pay for week {week}. Reason: Only earned {points_in_week}/{athlete.points_required} points.")
                        if MULTIPLIER_ON:
                            amount_to_pay += athlete.price_per_week * (MULTIPLIER ** price_multiplier)
                        else:
                            amount_to_pay += athlete.price_per_week
                        price_multiplier += 1
                    else:
                        week_results_dict[week] = 1  # Update week as passed
                        price_multiplier = 0

            amounts[athlete.username] = amount_to_pay

        return self.create_payment_embed(amounts, YEAR)


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

        # Sort amounts by value in descending order
        sorted_amounts = sorted(amounts.items(), key=lambda item: item[1], reverse=True)

        # Loop through the amounts and add fields to the embed
        for username, amount in sorted_amounts:
            if amount > 0:
                # Check if the amount is the max amount and add a special emoji
                emoji = "🤑" if amount == max_amount else ""
                embed.add_field(name=username, value=f"muas {amount}€ zoin.{emoji}", inline=False)
            else:
                embed.add_field(name=username, value=f"muas nix zoin.", inline=False)
        embed.add_field(name="Api requests", value=f"{self.num_of_API_requests} Weeks requested from the strava API. \n{self.num_of_retrieve_Cache} Weeks retrieved from cache.\n", inline=False)


        return embed
