"""
help.py

This module contains functions for handling the help command

Author: Julian Friedl
"""

import discord
import logging

from config.log_config import setup_logging


# Set up logging at the beginning of your script
setup_logging()

# Now you can use logging in this module
logger = logging.getLogger(__name__)

def help_embed():
    """
        Create a Discord Embed object for the help command.
    """
    logger.info("Help Command used.")
    embed = discord.Embed(title="Available Commands:", color=0x0073FF)

    embed.add_field(
        name="/strava_auth",
        value="- *Initiates the Strava authorization process.*\n"
              "- *Example:* `/strava_auth`",
        inline=False)
    
    embed.add_field(
        name="/week",
        value="- *Parameter:* Week (an integer in range 1-52)\n"
              "- *Returns:* The people who need to pay in the specified calendar week\n"
              "- *Example:* `/week 2`",
        inline=False)

    embed.add_field(
        name="/total",
        value="- *Parameter:* None\n"
              "- *Returns:* The total amount of money each participant has to pay\n"
              "- *Example:* `/total`",
        inline=False)
    
    embed.add_field(
        name="/joker",
        value="- *Parameter:* None\n"
              "- *Usage:* Skip the current Calender Week. Using it again will remove the Joker from the week.\n"
              "- *Example:* `/joker`",
        inline=False)

    return embed