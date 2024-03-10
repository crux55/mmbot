import discord
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True)

guild_ids = ['YYY']

@slash.slash(name="createevent",
             description="Create a new event",
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
               )
             ], guild_ids=guild_ids)
async def createevent(ctx: SlashContext, title: str, description: str):
    # Get the user who created the event
    event_creator = ctx.author

    # Send event details to mod channel for approval
    mod_channel = client.get_channel('mod-channel-id')  # Replace with your mod channel id
    button_row = create_actionrow(
        create_button(style=ButtonStyle.green, label="Approve", custom_id=f"approve:{title}:{description}:{event_creator.id}"),
        create_button(style=ButtonStyle.red, label="Reject", custom_id="reject")
    )
    await mod_channel.send(f"New event:\n**{title}**\n{description}\nCreated by: {event_creator.mention}", components=[button_row])
    await ctx.send(content='Event submitted for approval.', hidden=True)

@client.event
async def on_component(ctx: SlashContext):
    if ctx.custom_id.startswith('approve:'):
        # Get event details from custom_id
        _, title, description, creator_id = ctx.custom_id.split(':')

        # Create thread for event
        forum_channel = client.get_channel('forum-channel-id')  # Replace with your forum channel id
        thread = await forum_channel.create_thread(name=title)
        await thread.send(f"**{title}**\n{description}\nCreated by: <@{creator_id}>")

        await ctx.send(content='Event approved and thread created.', hidden=True)
    elif ctx.custom_id == 'reject':
        await ctx.send(content='Event rejected.', hidden=True)

client.run('your-bot-token')  # Replace with your bot token