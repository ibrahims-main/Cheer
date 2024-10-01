import discord
from discord.ext import commands
from utils.other.log_channel import log_channel
from discord import app_commands

class Unlock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="unlock", description="Unlocks the current channel, allowing users to send messages.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        everyone_role = interaction.guild.default_role

        # Check if the channel is already unlocked
        overwrites = interaction.channel.overwrites_for(everyone_role)
        if overwrites.send_messages is None or overwrites.send_messages is True:
            await interaction.response.send_message("This channel is already unlocked.", ephemeral=True)
            return

        # Modify the permissions to unlock the channel
        overwrites.send_messages = True
        await interaction.channel.set_permissions(everyone_role, overwrite=overwrites)

        # Send confirmation message
        await interaction.response.send_message(f"🔓 {interaction.channel.mention} has been unlocked.")

        await log_channel(
            title=None,
            description=f"{interaction.channel.mention} has been unlocked by {interaction.user.mention}.",
            guild=interaction.guild,
            color=discord.Color.green() 
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Unlock(bot))