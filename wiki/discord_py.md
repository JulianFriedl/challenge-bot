# Introduction to discord.py and Application Commands  (Version: 1.7.3)

`discord.py` is a modern, easy-to-use Python library that allows you to interact with the Discord API. With it, you can create bots, manage servers, send messages, and more. One of the features introduced in recent versions of the library is Application Commands (often referred to as slash commands due to their `/` prefix in Discord).

This document will provide a brief overview of `discord.py` (Version: 1.7.3), focusing on Application Commands and how they were utilized in a provided code.


## Basics of discord.py

Before delving into the specific functionalities of Application Commands, it's important to understand some basics of `discord.py`.

- **Client**: Represents a connection to Discord. This is the primary interface to interact with the Discord API.
  
- **Event**: A mechanism to react to changes or actions in Discord. Examples include `on_ready` (triggered when the bot is ready) and `on_message` (triggered upon receiving a message).
  
- **Guild**: Refers to a server in Discord.



## Application Commands in discord.py

Application commands allow users to interact with your bot by selecting a command from a dropdown list, rather than typing out the entire command. This provides a more user-friendly and intuitive experience.



### Setting up Application Commands

To use Application Commands, you'll need to set up the `CommandTree`. It's a special class in `discord.py` designed to hold all the state and information required for application commands. If you're using the `discord.Client`, you maintain your own tree, but if you're using `commands.Bot`, the bot will maintain its own tree.

**When using discord.Client:**
```python
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(Client)
```
**When using commands.Bot:**
```python
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
# tree can be accessed with bot.tree, for example 
@bot.tree.command(name = "help", description = "Displays every command and how to use it.")
async def help_command(interaction):
    """Slash Command Implementation of the help_command"""
    await interaction.response.send_message(embed=help_embed(), ephemeral= True)
```
---
### Synchronizing Commands

Commands can be synchronized to specific guilds for faster testing since global commands might take up to an hour to propagate.

**Using discord.Client**
```python
@client.event
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
```
**Or you can sync them globaly like this when using commands.Bot:**

```python
@bot.event
async def on_ready():
    await bot.tree.sync()
```

You can implement either option using both discord.Client or discord.Bot

---

### Defining Commands

Commands are defined using decorators. The primary decorator for this is `@client.tree.command()`. 

For example:

**Using discord.Client:**
```python
@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')
```

**Using commands.Bot:**
```python
@bot.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')
```

Parameters for the commands can be described for a more user-friendly experience on Discord.

```python
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
```

#### Optional args

To make an argument optional, you can either give it a supported default argument,
or you can mark it as Optional from the typing standard library. This example does both.

```python
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')
```

---

### Transformers

Transformers dictate how parameters in your code should behave both when used on Discord and when received from Discord. 

- **Built-in Transformers**: These are transformers provided by `discord.py`. An example is `app_commands.Range` which restricts the range of valid inputs.

**Example:**
```python
@bot.tree.command(name = "week", description = "Returns the people who need to pay in the specified calendar week")
@app_commands.describe(week_parameter='*Parameter:* Week (an integer in range 1-52)')
async def strava_auth_command(interaction, week_parameter:app_commands.Range[int, 1, 52]):
    """Slash Command Implementation of the week_command"""
    week_command = WeekCommand(week_parameter)
    await interaction.response.send_message(embed= week_command.get_who_needs_to_pay())
```
---

### Custom Transformers

Transformers are a way to convert or validate incoming data from a command's arguments. They're especially useful when you want to handle a specific format or transform a simple type into a more complex object.

#### 1. Basic Custom Transformer

Here's an example with a `Point` named tuple and its corresponding transformer `PointTransformer`:

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

class PointTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> Point:
        (x, _, y) = value.partition(',')
        return Point(x=int(x.strip()), y=int(y.strip()))
```

This transformer takes a string `value` formatted as "x,y" and returns a `Point` object.

#### 2. Inline Transformers

For simpler transformers that convert a string into a custom object, you can use inline transformers. This is done by defining a classmethod named `transform` directly within the custom type:

```python
class Point3D(NamedTuple):
    x: int
    y: int
    z: int

    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str):
        x, y, z = value.split(',')
        return cls(x=int(x.strip()), y=int(y.strip()), z=int(z.strip()))
```

In this example, `Point3D` takes a string formatted as "x,y,z" and returns a `Point3D` object.

---

### Usage in Commands

To use these transformers in commands, employ the `app_commands.Transform` type hint:

```python
@bot.tree.command()
async def graph(
    interaction: discord.Interaction,
    point: app_commands.Transform[Point, PointTransformer],
):
    await interaction.response.send_message(str(point))
```

For inline transformers:

```python
@bot.tree.command()
async def graph3d(interaction: discord.Interaction, point: Point3D):
    await interaction.response.send_message(str(point))
```
---
### Using Enums for Choices

Enums, short for "Enumerations," are a set of symbolic names (members) bound to unique, constant values. They can be used in `discord.py` to restrict choices a user can pick when interacting with a command. 

Here is an example using the `Fruits` Enum:

```python
from enum import Enum

class Fruits(Enum):
    apple = 0
    banana = 1
    cherry = 2
    dragonfruit = 3

@client.tree.command()
@app_commands.describe(fruit='The fruit to choose')
async def fruit(interaction: discord.Interaction, fruit: Fruits):
    """Choose a fruit!"""
    await interaction.response.send_message(str(fruit))
```

Here's what's happening:

1. An Enum `Fruits` is defined with four members: `apple`, `banana`, `cherry`, and `dragonfruit`.
2. This Enum is then used as a type hint in the `fruit` command. 
3. When users interact with this command in Discord, they'll see a dropdown list with four choices (`apple`, `banana`, `cherry`, and `dragonfruit`).
4. Once a user selects a choice and executes the command, the code receives the corresponding Enum member (e.g., `Fruits.apple` if they chose "apple").

---

### Context Menu Commands 

A Context Menu command allows users to run app commands by right-clicking on a member or message in the Discord client, then selecting from a context-sensitive menu.

#### **How to Create a Context Menu Command**

There are two main types of context menu commands: those that operate on members (users) and those that operate on messages. 

#### **1. Member Context Menu Command**

For a context menu command that works on members, use the `@client.tree.context_menu` decorator with the `name` parameter.

**Example: Show Join Date of a Member**

```python
@bot.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')
```

- **Description**: This command shows the date a member joined the server.
- **Usage**: Right-click on a member's name/avatar and select "Show Join Date" from the context menu.

#### **2. Message Context Menu Command**

For a context menu command that works on messages, you'll again use the `@client.tree.context_menu` decorator, but this time, the function will handle a `message` parameter.

**Example: Report a Message to Moderators**

```python
@bot.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # ... (handling report logic)
```

- **Description**: This command allows users to report a specific message to moderators.
- **Usage**: Right-click on a message and select "Report to Moderators" from the context menu. 

#### **Handling a Message Report**

In the provided code, once a message is reported:

1. A confirmation is sent to the user who executed the command. This message is ephemeral, meaning only the executor can see it.
2. The reported message details are then sent to a specific channel for moderators or administrators to review.

```python
    log_channel = interaction.guild.get_channel(0)  # Replace with your actual log channel's ID

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)
```

The report consists of an embed detailing the message, the author, and the time the message was sent. Additionally, a button is provided to directly jump to the reported message in its original context.

### Conclusion

`discord.py` offers a wide range of functionalities to create interactive and feature-rich Discord bots. Application commands, in particular, provide a more intuitive user experience.