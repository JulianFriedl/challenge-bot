from flask import request
import logging
from traceback import format_exc
from src.bot.commands.strava_auth_command import exchange_code

# Initialize logger
logger = logging.getLogger(__name__)

def strava_auth():
    """
    Handles incoming requests at the /strava_auth endpoint.
    """
    code = request.args.get('code')
    discord_user_id = request.args.get('discord_id')
    if code:
        try:
            exchange_code(code, discord_user_id)
            return 'Authorization successful! You can close this window.'
        except Exception as e:
            logger.error(f"An error occurred: {e}\n{format_exc()}")
            return 'An error occurred while processing the authorization. You can close this window.'
    else:
        return 'Authorization declined! You can close this window.'
