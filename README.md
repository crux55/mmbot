# Discord Event Bot

This is a Discord bot that allows users to create events, which can then be approved or rejected by moderators. The bot also handles the addition of users to scheduled events.

## Setup

1. Install the required packages with pip:

```bash
pip install -r requirements.txt
```

2. Create a .env file in the same directory as your script, and add your variables to it:

GUILD_ID=your_guild_id
FORUM_CHANNEL_ID=your_forum_channel_id
ADMIN_CHANNEL_ID=your_admin_channel_id
CHEESECAKE_USER_ID=your_cheesecake_user_id
BOT_CHANNEL_ID=your_bot_channel_id
BOT_TOKEN=your_bot_token

3. Run the bot

```bash
python bot.py
```


## Commands

- `/modsay #channel "Your message here"`: Send a message as the bot to a specific channel. You must have the "Moderator" role to use this command.

- `/create_event "event name" "event description" "dd/mm/yyyy HH:mm" "dd/mm/yyyy HH:mm" "location"`: Create a new event. This command takes five parameters: name, description, start time, end time, and location.

## Event Approval

When a user creates an event, the bot sends an approval request to the moderators. The moderators can then approve or reject the event. If the event is approved, the bot creates a thread for the event and a scheduled event.

## Error Handling

The bot logs informational and error messages to a file named bot.log. If an error occurs, the bot sends a notification to the bot channel.