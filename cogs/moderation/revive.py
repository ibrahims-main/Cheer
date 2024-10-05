import discord
from discord.ext import commands
from discord import app_commands
from utils.other.CooldownHandler import cooldown_check

class Revive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="revive", description="Revive the server.")
    @cooldown_check(14400) # 4 hours
    async def revive(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name="Chat Revival Ping")
        await interaction.response.send_message(f"{role.mention} WAKE UP DUMBOS")

async def setup(bot: commands.Bot):
    await bot.add_cog(Revive(bot))