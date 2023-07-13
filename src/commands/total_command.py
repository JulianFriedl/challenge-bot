import datetime
import time
import requests
import json
import discord

import services.auth_refresh as auth_refresh
import services.auth_data_controller as auth_data_controller
import commands.week_command as week_command
from utils.api_error_calls import api_request
from constants import CHALLENGE_START_WEEK, PRICE_PER_WEEK

def get_yearly_payments() -> discord.Embed:
    """
    Check yearly payments for each athlete and return a message indicating
    whether they need to pay or not for the current year. 
    """
    current_date = datetime.date.today()
    current_year = current_date.year
    current_week = datetime.date.today().isocalendar()[1]

    start_date = datetime.date(current_year, 1, 1)
    end_date = datetime.date(current_year, 12, 31)

    start_date_seconds = time.mktime(start_date.timetuple())
    end_date_seconds = time.mktime(end_date.timetuple())

    loaded_creds = auth_data_controller.load_credentials()

    if loaded_creds is None:
        return create_payment_embed('There are no authenticated athletes, please use the !strava_auth command.')

    amounts = {}

    for cred in loaded_creds:
        cred = auth_refresh.refresh_token(cred)
        auth_data_controller.save_credentials(json.dumps(cred))
        username = cred["athlete"]["username"]
        access_token = cred["access_token"]

        activities, error_embed = fetch_athlete_activities(username, access_token, start_date_seconds, end_date_seconds, end_date)

        if error_embed is not None:
            return error_embed

        amount_to_pay = 0

        for week in range(CHALLENGE_START_WEEK, current_week):
            points_in_week = week_command.WeekCommand(week).get_points(activities, username)
            if points_in_week < (week_command.WeekCommand.POINTS_REQUIRED if week >= 9 else 2):
                print(f"{username} has to pay in week {week} because they only earned {points_in_week} points.")
                amount_to_pay += PRICE_PER_WEEK

        amounts[username] = amount_to_pay

    return create_payment_embed(amounts, current_year)


def fetch_athlete_activities(username: str, access_token: str, start_date_seconds: int, end_date_seconds: int, end_date: datetime) -> tuple:
    activities = []
    page = 1
    per_page = 30
    end_of_results = False

    while not end_of_results:
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"before": end_date_seconds, "after": start_date_seconds, "page": page, "per_page": per_page}

        data, error_embed = api_request("https://www.strava.com/api/v3/athlete/activities", headers, params, username)

        if error_embed is not None:
            return activities, error_embed

        if not data:
            end_of_results = True
        else:
            activities.extend(data)

            page += 1

            for activity in data:
                activity_date_str = activity["start_date_local"][:10]
                activity_date = datetime.date.fromisoformat(activity_date_str)

                if activity_date > end_date:
                    end_of_results = True
                    break

    return activities, None

def create_payment_embed(amounts: dict, year: int) -> discord.Embed:
    """
    Create a Discord Embed object based on the payment details of each athlete in the current year.
    """
    embed = discord.Embed(
        title = f"Payment Details for {year}",
        description = "Yearly payment summary for all athletes.",
        color = discord.Color.blue()
    )

    for username, amount in amounts.items():
        if amount > 0:
            embed.add_field(name=username, value=f"muas {amount} euros für {year} zahlen.", inline=False)
        else:
            embed.add_field(name=username, value=f"muas nix für {year} zahlen.", inline=False)

    return embed
