from discord import Color, Embed, Guild

async def log_channel(title: str, guild: Guild, description: str, color: Color):
    log_channel = guild.get_channel(1290309804513820725)
    embed = Embed(
        title=title,
        description=description,
        color=color
    )

    await log_channel.send(embed=embed)