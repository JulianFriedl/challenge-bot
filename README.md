# challenge-bot
A bot for discord, that connects to strava api and retrieves and evaluates certain data for a strava challenge between friends. It authenticates the Strava API access using Oauth2. After the user grants permission to the bot it uses a Flask web server to handle the redirect from the Strava authorization page and extracts the code.


## Requirements

- Python 3.8 or higher
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
CLIENT_ID=YOUR_STRAVA_CLIENT_ID
CLIENT_SECRET=YOUR_STRAVA_CLIENT_SECRET
REDIRECT_URI=http://YOUR_ADDRESS/strava_auth
```

## Usage

- Run the `bot_app.py` script to start the Discord bot and the Flask web server
- Invite the bot to your Discord server using the following URL, replacing `YOUR_CLIENT_ID` with your Discord bot client ID:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot
```

- To link your Strava account to the bot, send a `!strava_auth` command to the bot in a direct message. The bot will send you a link to the Strava authorization page, where you can grant permission for the bot to access your data.
- After granting permission, you will be redirected back to the Flask web server, which will extract the authorization code from the request and pass it back to the bot.
- The bot will exchange the authorization code for an access token and use it to make requests to the Strava API on your behalf. You can then use other commands that evaluate the registered users performance in the challenge.
