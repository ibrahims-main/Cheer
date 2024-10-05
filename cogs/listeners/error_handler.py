import discord
from discord import app_commands
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            missing = ", ".join(error.missing_permissions)
            await interaction.response.send_message(f"❌ WOMP WOMP You are missing the following permissions to run this command: {missing}", ephemeral=True)

        elif isinstance(error, app_commands.BotMissingPermissions):
            missing = ", ".join(error.missing_permissions)
            await interaction.response.send_message(f"❌ 😭😭I'm missing the following permissions to run this command: {missing}", ephemeral=True)

        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"❌ Command on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)

        elif isinstance(error, app_commands.CommandNotFound):
            await interaction.response.send_message(f"❌ Command not found.", ephemeral=True)

        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(f"❌ LMAO You don't meet the required permissions to run this command.", ephemeral=True)

        elif isinstance(error, app_commands.CommandInvokeError):
            await interaction.response.send_message(f"❌ An error occurred while executing the command: {error.original}.", ephemeral=True)

        else:
            await interaction.response.send_message("❌ An unexpected error occurred. Please try again later.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))