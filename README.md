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
STRAVA_REDIRECT_URI=http://localhost:8000/strava_auth
```

## Usage

- Run the `discord_bot.py` script to start the Discord bot and the Flask web server
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
- `!week <Nr>`: Takes a Nr as param which is the desired calender week. Returns the people that need to pay in the specified week.
- `!total`: Returns all challenge members and the amount they have to pay.
