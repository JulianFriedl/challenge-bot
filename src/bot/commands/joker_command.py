"""
jocker_command.py

This module contains classes and functions for handling the joker command.

Author: Julian Friedl
"""

import datetime
import json
import discord
import logging

from src.shared.services.athlete_data_controller import load_athletes, update_athlete_vars
from src.shared.models.athlete import Athlete
from src.shared.config.log_config import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

class JokerCommand:

    def __init__(self, discord_user_id:str):
        current_date = datetime.datetime.now()
        logger.debug(f"Current date: {current_date}")
        self.week = current_date.isocalendar()[1]
        self.discord_user_id = discord_user_id

    def joker(self):
        logger.info("Joker Command called.")
        creds = load_athletes()
        athlete = None
        if creds:
            for cred in creds:
                if cred.get("discord_user_id", None) == self.discord_user_id:
                    athlete = Athlete(cred)
                    break
        
        if athlete is None:
            embed = discord.Embed(
                title="Registration Required",
                description=f"Discord User with ID `{self.discord_user_id}` is not registered.\nPlease use `/strava_auth` to register.",
                color=discord.Color.red()
            )
            return embed
        
        if self.week in athlete.joker_weeks:
            cred['vars']['joker_weeks'].remove(self.week)
            cred['vars']['joker'] += 1
            update_athlete_vars(cred)
            embed = discord.Embed(
                title="Joker Removed",
                description=f"Joker usage for week {self.week} removed.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Available Jokers", value=str(athlete.joker+1))
            return embed

        if athlete.joker <= 0:
            joker_weeks_str = ', '.join(map(str, athlete.joker_weeks))
            embed = discord.Embed(
                title="No Joker Uses Left",
                description=f"You have used all your Joker uses.\nPrevious usages: Week/s {joker_weeks_str}.",
                color=discord.Color.orange()
            )
            return embed

        cred['vars']['joker_weeks'].append(self.week)
        cred['vars']['joker'] -= 1
        update_athlete_vars(cred)

        embed = discord.Embed(
            title="Joker Used",
            description=f"Joker used for Week {self.week}.",
            color=discord.Color.purple()
        )
        embed.add_field(name="Remaining Jokers", value=str(athlete.joker-1))
        return embed