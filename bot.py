import datetime
import uuid
import dataclasses
import discord
from discord.ext import commands
import pickle
import logging
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the variables
GUILD_ID = os.getenv('GUILD_ID')
FORUM_CHANNEL_ID = os.getenv('FORUM_CHANNEL_ID')
ADMIN_CHANNEL_ID = os.getenv('ADMIN_CHANNEL_ID')
CHEESECAKE_USER_ID = os.getenv('CHEESECAKE_USER_ID')
BOT_CHANNEL_ID = os.getenv('BOT_CHANNEL_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# File names
EVENTS_FILE_NAME = "events.pkl"

# Time constants
ONE_DAY_IN_SECONDS = 60 * 60 * 24

# Bot settings
intents = discord.Intents.all()
intents.message_content = True
intents.guild_scheduled_events = True

# Global variables
EVENTS = []

# Create the bot
bot = commands.Bot(command_prefix="/", intents=intents)


# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler('bot.log')
handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)

def log_info(message):
    """
    Log an informational message.

    Args:
        message (str): The message to log.
    """
    logger.info(message)

def log_error(message):
    """
    Log an error message and send a notification to the bot channel.

    Args:
        message (str): The message to log.
    """
    bot.get_channel(BOT_CHANNEL_ID).send(f"User <@{CHEESECAKE_USER_ID}> there's been an error: {message}")
    logger.error(message)

def add_to_events(event):
    """
    Add an event to the EVENTS list and save the list to disk.

    Args:
        event (Event): The event to add.
    """
    EVENTS.append(event)
    save_events_to_disk(EVENTS)

def load_events():
    """
    Load the EVENTS list from disk.
    """
    global EVENTS
    EVENTS = load_events_from_disk()

def save_events_to_disk(events):
    """
    Save a list of events to disk.

    Args:
        events (list): The list of events to save.
    """
    try:
        with open(EVENTS_FILE_NAME, 'wb') as f:
            pickle.dump(events, f)
    except (pickle.PicklingError, OSError) as e:
        #TODO: dump to text file
        log_error(f"Error saving events to disk: {e}")

def load_events_from_disk():
    """
    Load a list of events from disk.

    Returns:
        list: The list of events, or an empty list if the file doesn't exist or an error occurred.
    """
    try:
        with open(EVENTS_FILE_NAME, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []
    except (pickle.UnpicklingError, OSError) as e:
        log_error(f"Error loading events from disk: {e}")
        return []

def convert_string_to_dt(dt_string):
    """
    Convert a date and time string to a datetime object.

    The input string should be in the format 'dd/mm/yyyy hh:mm'. The returned datetime object
    will be "aware", i.e., it will have timezone information.

    Args:
        dt_string (str): The date and time string to convert.

    Returns:
        datetime.datetime: The converted datetime object
    """
    # Get the current local timezone
    local_tz = datetime.datetime.now().astimezone().tzinfo

    # Convert the string to a "naive" datetime object (without timezone info)
    naive_dt = datetime.datetime.strptime(dt_string, '%d/%m/%Y %H:%M')

    # Make the datetime object "aware" by adding the local timezone info
    aware_dt = naive_dt.replace(tzinfo=local_tz)

    return aware_dt

@dataclasses.dataclass
class Event:
    uuid: str
    name: str
    description: str
    start_time: str
    end_time: str
    location: str
    op_id: str
    op_name: str
    event_id: str = ""
    event_forum_url: str = ""
    event_forum_id: str = ""
    original_channel_id: str = ""

class Event_Approval_Message(discord.ui.View):
    """A view for approving events."""

    def __init__(self, event: Event):
        """
        Initialize the view with the given event.

        Args:
            event (Event): The event to be approved.
        """
        super().__init__()
        self.event = event
        self.timeout = ONE_DAY_IN_SECONDS

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button):
        """
        Handle the button click to approve an event.

        This method edits the interaction message, stops the view, creates a thread for the event,
        creates a scheduled event, and adds the event to the EVENTS list.

        Args:
            interaction (discord.Interaction): The interaction that triggered the button click.
            button (discord.ui.Button): The button that was clicked.
        """
        try:
            # Get the user who clicked the button
            user = interaction.user

            # Edit the interaction message to show that the event was approved
            custom_id = f"The event {self.event.name} was approved by {user.global_name}"
            await interaction.message.edit(content=custom_id, view=None)
            self.stop()

            # Create a thread for the event
            thread_name = f"{self.event.start_time} | {self.event.name}"
            forum : discord.ForumChannel = bot.get_channel(FORUM_CHANNEL_ID)
            forum_info = await forum.create_thread(name=thread_name, content=f"{self.event.description}\n <@{self.event.op_id}> your event post is ready")
            created_thread = forum_info[0]

            # Update the event with the thread info
            self.event.event_forum_id = created_thread.id
            self.event.event_forum_url = created_thread.jump_url

            # Create a scheduled event
            event = await bot.get_guild(GUILD_ID).create_scheduled_event(
                name=self.event.name,
                start_time=self.event.start_time,
                location=self.event.location,
                end_time=self.event.end_time,
                description=f"{self.event.description} \n Checkout out the discussion thread [here]({created_thread.jump_url})!\n Point for contact for this event is <@{self.event.op_name}>.",
                entity_type=discord.EntityType.external,
                privacy_level=discord.PrivacyLevel.guild_only
            )

            # Update the event with the scheduled event info
            self.event.event_id = event.id

            # Add the event to the EVENTS list
            add_to_events(self.event)
        except Exception as e:
            log_error(f"Error in button_callback: {e}")


    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, custom_id="reject")
    async def on_reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Handle the button click to reject an event.

        This method edits the interaction message to show that the event was rejected and stops the view.

        Args:
            interaction (discord.Interaction): The interaction that triggered the button click.
            button (discord.ui.Button): The button that was clicked.
        """
        try:
            # Get the user who clicked the button
            user = interaction.user

            # Edit the interaction message to show that the event was rejected
            custom_id = f"The event {self.event.name} was rejected by {user.name}"
            await interaction.message.edit(content=custom_id, view=None)

            # Stop the view
            self.stop()
            bot.get_channel(self.event.original_channel_id).send(f"Event {self.event.name} was rejected."
        except Exception as e:
            log_error(f"Error in on_reject: {e}")

@bot.command()
async def modsay(ctx, channel: discord.TextChannel = None, *, message = None):
    """
    Send a message as the bot to a specific channel.

    Args:
        ctx (discord.ext.commands.Context): The context in which the command was called.
        channel (discord.TextChannel): The channel to send the message to.
        message (str): The message to send.
    """
    # Check if the first parameter is "help"
    if channel == "help":
        await ctx.send('Usage: /modsay #channel "Your message here"')
        return

    # Check if the user has the "Moderator" role
    if any(role.name == "Moderator" for role in ctx.author.roles):
        if channel and message:
            await bot.get_channel(channel.id).send(message)
        else:
            await ctx.send('Missing parameters. Usage: /modsay #channel "Your message here"')
    else:
        await ctx.send("You do not have permission to use this command.")

@bot.command()
async def create_event(ctx, name=None, description=None, start_time=None, end_time=None, location=None):
    """
    Create a new event.

    This command takes five parameters: name, description, start_time, end_time, and location. If any of these
    parameters is missing, it sends an error message. If all parameters are provided, it creates a new Event
    object and sends an approval request.

    Args:
        ctx (discord.ext.commands.Context): The context in which the command was called.
        name (str): The name of the event.
        description (str): The description of the event.
        start_time (str): The start time of the event, in the format 'dd/mm/yyyy HH:mm'.
        end_time (str): The end time of the event, in the format 'dd/mm/yyyy HH:mm'.
        location (str): The location of the event.
    """
    # Check that all parameters are provided
    error_message = ""
    if name is None:
        error_message += "Name is required\n"
    if description is None:
        error_message += "Description is required\n"
    if start_time is None:
        error_message += "Start time is required\n"
    if end_time is None:
        error_message += "End time is required\n"
    if location is None:
        error_message += "Location is required\n"

    # If any parameters are missing, send an error message and return
    if error_message:
        error_message += 'The order of the params is name, description, start time, end time, location.\nExample: /create_event "event name" "event description" "dd/mm/yyyy HH:mm" "dd/mm/yyyy HH:mm" "location"'
        await ctx.send(error_message)
        return

    # Convert the start and end times to datetime objects
    try:
        start_time = convert_string_to_dt(start_time)
        end_time = convert_string_to_dt(end_time)
    except ValueError as e:
        await ctx.send(f"At least one of the date strings you gave contains an issue: {str(e)}")
        return

    # Create a new Event object
    event = Event(uuid.uuid4(), name, description, start_time, end_time, location, ctx.author.id, ctx.author.name, ctx.channel.id)

    # Send an approval request
    await ctx.send(
        f"Event {event.name} approval request. This event was created by @<{ctx.author.id}> and is scheduled to start at {event.start_time} and end at {event.end_time} at {event.location}.\n It's described as {event.description}.\n Please approve or reject this event.",
        view=Event_Approval_Message(event),
    )

@bot.event
async def on_scheduled_event_user_add(event, user):
    """
    Handle the addition of a user to a scheduled event.

    This method checks if the user is already in the event. If not, it sends a message to the event's forum channel.

    Args:
        event (discord.ScheduledEvent): The scheduled event.
        user (discord.User): The user who was added to the event.
    """
    try:
        for _event in EVENTS:
            # Get the users in the event
            users = []
            async for user in bot.get_guild(GUILD_ID).get_scheduled_event(event.id).users():
                users.append(user)

            # Check if the user is already in the event
            user_in_users = user.id in [u.id for u in users]

            # If the user is not in the event, send a message to the event's forum channel
            if _event.event_id == event.id and not user_in_users:
                await bot.get_channel(_event.event_forum_id).send(f"User <@{user.id}> has joined the event {_event.name} at {_event.start_time} at {_event.location}.")
    except Exception as e:
        log_error(f"Error in on_scheduled_event_user_add: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    EVENTS = load_events()
    print("Ready!")

# Run the bot with your token
bot.run(BOT_TOKEN)