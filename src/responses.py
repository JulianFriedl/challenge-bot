"""
file: command_responses.py

description: This module handles responses to commands given to the Discord bot.

Author: Julian Friedl
"""

import discord 

from commands.week_command import WeekCommand
import commands.strava_auth_command as StravaAuth
from commands.total_command import TotalCommand

def help_embed():
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




def handle_response(message) -> str:
    """
    Handles responses to commands given to the Discord bot.

    This function processes messages given to the bot, 
    and calls the appropriate command function to generate a response.
    """
    p_message = str(message.lower())

    if p_message.startswith('!week'):
        is_valid, week = parse_week_input(message)
        if is_valid:
            week_command = WeekCommand(week)
            return week_command.get_who_needs_to_pay()
        else:
            embed = discord.Embed(title="Invalid parameter!",
                description="Invalid Parameter!\nMake sure command is of type:\n!week <Nr>, Nr...A Number indicating the calendar week in range(1,52).",
                color=discord.Color.red())
            return embed       
    elif p_message == '!total':
        total_command = TotalCommand()
        return total_command.get_yearly_payments()
    elif p_message == '!strava_auth':
        return StravaAuth.strava_auth()
    elif p_message == '!help':
        return help_embed()
    return ''

def parse_week_input(message):
    """
    Parses the week number from the input message.
    
    This function takes the message, splits it into parts, 
    and checks if it is a valid '!week' command.
    """
    parts = message.split()
    if len(parts) != 2:
        return (False, None)
    command, week_str = parts
    if command != "!week":
        return (False, None)
    try:
        week = int(week_str)
    except ValueError:
        return (False, None)
    if not 1 <= week <= 52:
        return (False, None)
    return (True, week)
