import discord
from discord.ext import commands
from utils.views.SuggestionView import SuggestionModal
from discord import app_commands

class Suggestion(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="suggest", description="Give your  \"great\" suggestions")
    async def suggest(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SuggestionModal())

async def setup(bot: commands.Bot):
    await bot.add_cog(Suggestion(bot))