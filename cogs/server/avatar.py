import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

class Avatar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="View your or someone else's avatar")
    async def avatar(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        member = member or interaction.user

        embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.random())
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Avatar(bot))