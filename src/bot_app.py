"""
file: challenge_bot_app.py

description: This script is the main entry point for the Discord bot. It handles setup, runs the bot, and
routes messages to the appropriate handlers.

Author: Julian Friedl
"""

import os
from dotenv import load_dotenv
import discord
import responses

from flask_app import start_flask  # Consider renaming this to be snake_case


# Load environment variables from .env file
load_dotenv()

# Get the Discord token from the .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Get the Client object from discord.py. Client is synonymous with Bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    """
    Event listener for when the bot has switched from offline to online.
    It starts up the Webserver that is used for retrieving Strava auth
    """
    start_flask()
    print(f'{bot.user} is now running!')

@bot.event
async def on_message(message):
    """
    Event listener for when a new message is sent to a channel.
    It checks if the message is from the bot and ignores it if true,
    then handles responses if a message was received.
    """
    # Check if the message is from the bot
    if message.author == bot.user:
        return

    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f"{username} said : '{user_message}' ({channel})")
    
    try:
        response = responses.handle_response(user_message)
        if response:
             if isinstance(response, discord.Embed):
                 await message.channel.send(embed=response)
             else:
                 await message.channel.send(response)
    except Exception as e:
         print(e)
	


# Execute the bot with the specified token
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

