# challenge-bot

A bot for Discord, that connects to the Strava API and retrieves and evaluates certain data for a Strava challenge between friends. It authenticates the Strava API access using OAuth2. After the user grants permission to the bot, it uses a Flask web server to handle the redirect from the Strava authorization page and extracts the code.

## Requirements

- Python 3.8 or higher
- A Discord bot account and token
- A Strava application with a client ID and secret

## Installation

### Clone or Download the Repository

```bash
git clone https://github.com/yourusername/challenge-bot.git
cd challenge-bot
```

### Set Up a Python Virtual Environment

It's recommended to use a virtual environment for Python projects to manage dependencies separately for each project.

1. **Create a Virtual Environment**

```bash
python3 -m venv venv
```

2. **Activate the Virtual Environment**

- On Linux or macOS:

  ```bash
  source venv/bin/activate
  ```

- On Windows:

  ```cmd
  venv\Scripts\activate.bat
  ```

### Install Required Libraries

With the virtual environment activated, install the required libraries using `pip`:

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project directory and add your Discord bot token, Strava client ID and secret, and redirect URI as environment variables:

```plaintext
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
CLIENT_ID=YOUR_STRAVA_CLIENT_ID
CLIENT_SECRET=YOUR_STRAVA_CLIENT_SECRET
REDIRECT_URI=http://YOUR_ADDRESS/strava_auth
PORT=YOUR_PORT
```

## Usage

With the virtual environment activated, run the `bot_app.py` script to start the Discord bot and the Flask web server:

```bash
python bot_app.py
```

### Invite the Bot to Your Discord Server

Use the following URL, replacing `YOUR_CLIENT_ID` with your Discord bot client ID, to invite the bot to your Discord server:

```url
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot
```

### Link Your Strava Account

- Send a `/strava_auth` command to the bot in a direct message. The bot will send you a link to the Strava authorization page.
- Grant permission for the bot to access your data.
- You'll be redirected back to the Flask web server, which will extract the authorization code and pass it back to the bot.
- The bot will exchange the authorization code for an access token and use it to make requests to the Strava API on your behalf.

Now, your setup should be complete, and you can use the bot to evaluate the performance of registered users in the challenge.
