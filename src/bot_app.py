"""
file: challenge_bot_app.py

description: This script is the main entry point for the Discord bot. It handles setup, runs the bot, and
routes messages to the appropriate handlers.

Author: Julian Friedl
"""

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

from flask_app import start_flask  # Consider renaming this to be snake_case
from commands.help_command import help_embed
import commands.strava_auth_command as StravaAuth
from commands.total_command import TotalCommand
from commands.week_command import WeekCommand



# Load environment variables from .env file
load_dotenv()

# Get the Discord token from the .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Get the Client object from discord.py. Client is synonymous with Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    """
    Event listener for when the bot has switched from offline to online.
    It starts up the Webserver that is used for retrieving Strava auth
    """
    await bot.tree.sync()
    start_flask()
    print(f'{bot.user} is now running!')


@bot.tree.command(name = "help", description = "Displays every command and how to use it.")
async def help_command(interaction):
    """Slash Command Implementation of the help_command"""
    await interaction.response.send_message(embed=help_embed(), ephemeral= True)

@bot.tree.command(name = "strava_auth", description = "Initiates the Strava authorization process.")
async def strava_auth_command(interaction):
    """Slash Command Implementation of the strava_auth_command"""
    await interaction.response.send_message(embed=StravaAuth.strava_auth(), ephemeral= True)

@bot.tree.command(name = "week", description = "Returns the people who need to pay in the specified calendar week")
@app_commands.describe(week_parameter='*Parameter:* Week (an integer in range 1-52)')
async def strava_auth_command(interaction, week_parameter:app_commands.Range[int, 1, 52]):
    """Slash Command Implementation of the week_command"""
    week_command = WeekCommand(week_parameter)
    await interaction.response.send_message(embed= week_command.get_who_needs_to_pay())

@bot.tree.command(name = "total", description = "Returns all challenge members and the amount they have to pay.")
async def strava_auth_command(interaction):
    """Slash Command Implementation of the total_command"""
    total_command = TotalCommand()
    await interaction.response.send_message(embed=total_command.get_yearly_payments())

# Execute the bot with the specified token
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

