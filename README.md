# challenge-bot
A bot for discord, that connects to strava api and retrieves and evaluates certain data. It uses OAuth 2.0 to authenticate with the Strava API and obtain access tokens on behalf of the users. It also uses a Flask web server to handle the redirect from the Strava authorization page.


## Requirements

- Python 3.6 or higher
- `discord.py` library
- `requests` library
- `flask` library
- `python-dotenv` library
- `waitress` library
- A Discord bot account and token
- A Strava application and client ID and secret

## Installation

- Clone or download this repository
- Install the required libraries using `pip install -r requirements.txt`
- Create a `.env` file in the project directory and add your Discord bot token, Strava client ID and secret, and redirect URI as environment variables:

```
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
STRAVA_CLIENT_ID=YOUR_STRAVA_CLIENT_ID
STRAVA_CLIENT_SECRET=YOUR_STRAVA_CLIENT_SECRET
STRAVA_REDIRECT_URI=http://YOUR_ADDRESS/strava_auth
```

## Usage

- Run the `bot_app.py` script to start the Discord bot and the Flask web server
- Invite the bot to your Discord server using the following URL, replacing `YOUR_CLIENT_ID` with your Discord bot client ID:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot
```

- To link your Strava account to the bot, send a `!strava_auth` command to the bot in a direct message. The bot will send you a link to the Strava authorization page, where you can grant permission for the bot to access your data.
- After granting permission, you will be redirected back to the Flask web server, which will extract the authorization code from the request and pass it back to the bot.
- The bot will exchange the authorization code for an access token and use it to make requests to the Strava API on your behalf. You can then use other commands to about the challenge.

## Commands

The following commands are available for the bot:

- `!strava_auth`: Sends a link to the Strava authorization page, where you can grant permission for the bot to access your data. And exchanges the authorization code for an access token and stores it for future requests. You need to provide the authorization code that you received after granting permission.
- `!strava_code <code>`: Exchanges the authorization code for an access token and stores it for future requests. You need to provide the authorization code that you received after granting permission.
- `!week <Nr>:` This command requires a calendar week number as a parameter. When invoked, the bot performs several actions to provide data for the specified week:
    1. The bot checks if there are any registered athletes. If not, it notifies the user that there are no authenticated athletes and they should use the !strava_auth command.
    2. The bot validates if the requested week is not in the future. If the week is invalid, it returns an error.
    3. For each registered athlete, the bot retrieves the athlete's activities for the specified week. It calculates the points earned by the athlete based on the duration and type of each activity (using rules defined in the Activity class).
    4. The bot also counts the number of High-Intensity Training (HIT) workouts, with each pair of HIT workouts counting as an additional point. An activity must last at least 10 minutes but less than 60 minutes to be considered as a HIT workout.
    5. If an athlete performs a multi-day activity that lasts more than 6 hours past midnight, they earn an additional point for each day.
    6. If the total points earned by the athlete is less than 3 (or 2 if the week number is less than 9), the bot states that the athlete needs to pay. If the points are equal to or greater than the threshold, the bot states that the athlete does not need to pay.
    7. The command returns a Discord embed message with the payment details for each athlete for the week.
- `!total`: Returns all challenge members and the amount they have to pay.
    1. `get_yearly_payments():` Returns a Discord embed containing each athlete's annual payment information. The annual payment is calculated based on the number of weeks an athlete didn't meet the required activity points.
    2. `fetch_athlete_activities():` Retrieves an athlete's activity data for a specified year from the Strava API.
    3. `create_payment_embed():` Creates a Discord embed containing the total annual payment information for each athlete.