import os
from discord.ext.commands import Bot

async def loadAll(client: Bot):
    
    # leveling
    for level in os.listdir("./cogs/levels"):
        if level.endswith(".py"):
            await client.load_extension(f'cogs.levels.{level[:-3]}')
            print(f"Loaded: {level[:-3]}")

    # Tickets
    for ticket in os.listdir("./cogs/tickets"):
        if ticket.endswith(".py"):
            await client.load_extension(f'cogs.tickets.{ticket[:-3]}')
            print(f"Loaded: {ticket[:-3]}")

    # Moderation
    for mod in os.listdir("./cogs/moderation"):
        if mod.endswith(".py"):
            await client.load_extension(f'cogs.moderation.{mod[:-3]}')
            print(f"Loaded: {mod[:-3]}")

    # Fun
    for fun in os.listdir("./cogs/fun"):
        if fun.endswith(".py"):
            await client.load_extension(f'cogs.fun.{fun[:-3]}')
            print(f"Loaded: {fun[:-3]}")

    # Server
    for server in os.listdir("./cogs/server"):
        if server.endswith(".py"):
            await client.load_extension(f'cogs.server.{server[:-3]}')
            print(f"Loaded: {server[:-3]}")

    # Listeners
    for listener in os.listdir("./cogs/listeners"):
        if listener.endswith(".py"):
            await client.load_extension(f'cogs.listeners.{listener[:-3]}')
            print(f"Loaded: {listener[:-3]}")

    # Economy
    for economy in os.listdir("./cogs/economy"):
        if economy.endswith(".py"):
            await client.load_extension(f'cogs.economy.{economy[:-3]}')
            print(f"Loaded: {economy[:-3]}")