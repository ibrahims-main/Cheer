import discord
from discord import app_commands
from discord.ext import commands
from utils.other.log_channel import log_channel

class Lockdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="lockdown", description="Locks down the current channel, preventing users from sending messages.")
    @app_commands.checks.has_permissions(manage_channels=True)  # Requires manage channels permission
    async def lockdown(self, interaction: discord.Interaction):
        # Get the @everyone role
        everyone_role = interaction.guild.default_role

        # Check if the channel is already locked
        overwrites = interaction.channel.overwrites_for(everyone_role)
        if overwrites.send_messages is False:
            await interaction.response.send_message("This channel is already locked down.", ephemeral=True)
            return

        # Modify the permissions to lock the channel
        overwrites.send_messages = False
        await interaction.channel.set_permissions(everyone_role, overwrite=overwrites)

        # Send confirmation message
        await interaction.response.send_message(f"🔒 {interaction.channel.mention} has been locked down.")

        await log_channel(
            title=None,
            description=f"{interaction.channel.mention} has been locked down by {interaction.user.mention}.",
            guild=interaction.guild,
            color=discord.Color.green() 
        )

async def setup(bot):
    await bot.add_cog(Lockdown(bot))