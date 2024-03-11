import asyncio
from datetime import datetime, timedelta

# Store scheduled events in a dictionary
# Key: event start time, Value: event details
scheduled_events = {}

@client.slash_command(
    name="scheduleevent",
    description="Schedule a new event",
    options=[
        create_option(
            name="title",
            description="Title of the event",
            option_type=3,
            required=True
        ),
        create_option(
            name="description",
            description="Description of the event",
            option_type=3,
            required=True
        ),
        create_option(
            name="start_time",
            description="Start time of the event (YYYY-MM-DD HH:MM format)",
            option_type=3,
            required=True
        )
    ], guild_ids=guild_ids)
async def scheduleevent(ctx: SlashContext, title: str, description: str, start_time: str):
    # Parse the start time
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")

    # Store the event details
    scheduled_events[start_time] = {
        "title": title,
        "description": description,
        "creator": ctx.author.id
    }

    await ctx.send(content='Event scheduled.', hidden=True)

async def check_scheduled_events():
    while True:
        now = datetime.now()
        for start_time, event in list(scheduled_events.items()):
            if now >= start_time:
                # The event should start now
                forum_channel = client.get_channel('1216346127289421825')  # Replace with your forum channel id
                thread = await forum_channel.create_thread(name=event["title"])
                await thread.send(f"**{event['title']}**\n{event['description']}\nCreated by: <@{event['creator']}>")

                # Remove the event from the dictionary
                del scheduled_events[start_time]

        # Wait for a minute before checking again
        await asyncio.sleep(60)

# Start the task that checks for scheduled events
client.loop.create_task(check_scheduled_events())

client.run('your-bot-token')  # Replace with your bot token