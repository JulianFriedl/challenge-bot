"""
help.py

This module contains functions for handling the help command

Author: Julian Friedl
"""

import discord

def help_embed():
    """
        Create a Discord Embed object for the help command.
    """
    embed = discord.Embed(title="Available Commands:", color=0x0073FF)

    embed.add_field(
        name="!strava_auth",
        value="- *Initiates the Strava authorization process.*\n"
              "- *Example:* `!strava_auth`",
        inline=False)
    
    embed.add_field(
        name="!week",
        value="- *Parameter:* Week (an integer in range 1-52)\n"
              "- *Returns:* The people who need to pay in the specified calendar week\n"
              "- *Example:* `!week 2`",
        inline=False)

    embed.add_field(
        name="!total",
        value="- *Parameter:* None\n"
              "- *Returns:* The total amount of money each participant has to pay\n"
              "- *Example:* `!total`",
        inline=False)

    return embed