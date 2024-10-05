import discord
from discord.ext import commands
from discord import app_commands
from utils.views.AnnouncementView import AnnouncementModal

class Announcement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="announce", description="Sends an announcement to the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name="Announcement Ping")
        await interaction.response.send_message(f"{role.mention}")
        await interaction.response.send_modal(AnnouncementModal())

async def setup(bot: commands.Bot):
    await bot.add_cog(Announcement(bot))