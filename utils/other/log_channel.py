from discord import Color, Embed, Guild, File
from typing import Optional

async def log_channel(
    guild: Guild,
    description: str,
    color: Color,
    title: Optional[str] = None,  # Optional title with default value None
    file: Optional[File] = None   # Optional file with default value None
):
    log_channel = guild.get_channel(1290309804513820725)
    
    # Create the embed
    embed = Embed(
        description=description,
        color=color
    )
    
    # If a title is provided, set it in the embed
    if title:
        embed.title = title
    
    # Send the message, attaching the file if provided
    await log_channel.send(embed=embed, file=file if file else None)