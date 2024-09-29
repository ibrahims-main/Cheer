import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
from utils.other.load_cogs import loadAll
from utils.views.TicketView import CreateButton, CloseButton, TrashButton

load_dotenv()
TOKEN = getenv("TOKEN")

client = commands.Bot(command_prefix=":)", intents=discord.Intents.all(), help_command=None)

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")
    await loadAll(client=client)
    client.add_view(CreateButton())
    client.add_view(CloseButton())
    client.add_view(TrashButton())

    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

client.run(TOKEN)