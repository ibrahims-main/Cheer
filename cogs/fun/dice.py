import discord
import random
from discord import app_commands
from discord.ext import commands

class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dice", description="Rolls a six-sided die")
    async def dice(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You rolled: {random.randint(1, 6)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Dice(bot))