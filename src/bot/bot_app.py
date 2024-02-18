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
import traceback 

from src.shared.api.custom_api_error import CustomAPIError
from src.web.backend.flask_app import start_flask 
from src.bot.commands.joker_command import JokerCommand
from src.bot.commands.help_command import help_embed
from src.bot.commands.strava_auth_command import strava_auth
from src.bot.commands.total_command import TotalCommand
from src.bot.commands.week_command import WeekCommand
from src.shared.config.log_config import setup_logging
from src.shared.services.athlete_data_controller import clear_week_results


setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the Discord token from the .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_ADMIN_ID = os.getenv("DISCORD_ADMIN_ID")

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


@bot.tree.error
async def on_application_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global error handler for application commands."""
    # Assuming logger is already defined and configured
    error_traceback = traceback.format_exception(type(error), error, error.__traceback__)
    # Initialize error_embed outside the if-else scope
    error_embed = None
    
    # Customize error message or embed based on the exception type
    if isinstance(error.original, CustomAPIError):
        # Directly use the embed from the CustomAPIError
        logger.error(f"An error occurred: {error}")
        error_embed = error.original.embed
    else:
        # Handle other errors
        logger.error(f"An error occurred: {error_traceback}")
        message = "An internal error occurred."
        error_embed = discord.Embed(title="Internal Error", description=message, color=discord.Color.red())

    # Ensure error_embed is not None before attempting to send it
    if error_embed:
        # Check if the interaction has been responded to
        if interaction.response.is_done():
            # Use followup.send when the initial response has been made
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        else:
            # Use response.send_message for the initial response
            await interaction.response.send_message(embed=error_embed, ephemeral=True)



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
    embed_result = await loop.run_in_executor(None, WeekCommand(week_parameter).excecute_week_command)
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

@bot.tree.command(name="clear_weeks", description="Admin Command.")
async def clear_weeks(interaction: discord.Interaction):
    """Slash Command Implementation of Clear Week results"""
    discord_user_id = str(interaction.user.id)  # Ensure it's a string for comparison

    # Check if the user is not an admin
    if discord_user_id != DISCORD_ADMIN_ID:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # If the user is the admin, proceed with the command
    await interaction.response.defer(ephemeral=True)
    loop = asyncio.get_event_loop()

    # Assuming clear_week_results() is defined elsewhere and does not need arguments
    await loop.run_in_executor(None, clear_week_results)
    await interaction.followup.send("Weeks cleared.")



# Execute the bot with the specified token
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

