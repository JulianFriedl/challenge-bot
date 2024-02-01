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
import asyncio
import logging


from flask_app import start_flask  # Consider renaming this to be snake_case
from commands.joker_command import JokerCommand
from commands.help_command import help_embed
from commands.strava_auth_command import strava_auth
from commands.total_command import TotalCommand
from commands.week_command import WeekCommand
from config.log_config import setup_logging


# Set up logging at the beginning of your script
setup_logging()

# Now you can use logging in this module
logger = logging.getLogger(__name__)

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
    logger.info(f'{bot.user} is now running!')


@bot.tree.command(name = "help", description = "Displays every command and how to use it.")
async def help_command(interaction: discord.Interaction):
    """Slash Command Implementation of the help_command"""
    #response.defer() is used to give the bot more time to reply to the discord api
    #(default time is 3 seconds with the new slash commands before it throws 404 exception)
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(embed=help_embed(), ephemeral= True)

@bot.tree.command(name = "strava_auth", description = "Initiates the Strava authorization process.")
async def strava_auth_command(interaction: discord.Interaction):
    """Slash Command Implementation of the strava_auth_command"""
    discord_user_id = interaction.user.id
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(embed=strava_auth(discord_user_id), ephemeral= True)

@bot.tree.command(name="week", description="Returns the people who need to pay in the specified calendar week")
@app_commands.describe(week_parameter='*Parameter:* Week (an integer in range 1-52)')
async def week_command(interaction: discord.Interaction, week_parameter:app_commands.Range[int, 1, 52]):
    """Slash Command Implementation of the week_command"""
    await interaction.response.defer()
    loop = asyncio.get_event_loop()
    embed_result = await loop.run_in_executor(None, WeekCommand(week_parameter).get_who_needs_to_pay)
    await interaction.followup.send(embed=embed_result)

@bot.tree.command(name="total", description="Returns all challenge members and the amount they have to pay.")
async def total_command(interaction: discord.Interaction):
    """Slash Command Implementation of the total_command"""
    await interaction.response.defer()
    loop = asyncio.get_event_loop()
    embed_result = await loop.run_in_executor(None, TotalCommand().get_yearly_payments)
    await interaction.followup.send(embed=embed_result)

@bot.tree.command(name="joker", description="Allows you to skip a week.")
async def joker_command(interaction: discord.Interaction):
    """Slash Command Implementation of the joker_command"""
    discord_user_id = interaction.user.id
    await interaction.response.defer()
    loop = asyncio.get_event_loop()
    embed_result = await loop.run_in_executor(None, JokerCommand(str(discord_user_id)).joker)
    await interaction.followup.send(embed=embed_result)


# Execute the bot with the specified token
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

