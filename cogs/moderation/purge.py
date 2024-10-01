import discord
from discord.ext import commands
from discord import app_commands
from utils.other.log_channel import log_channel
import os

class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Clear a specified number of messages.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()

        # Purge messages
        deleted = await interaction.channel.purge(limit=amount)
        
        # Prepare log content
        log_content = "Purged Messages Log\n\n"
        for message in deleted:
            log_content += f"Author: {message.author} | Time: {message.created_at} | Content: {message.content}\n"
        
        # Save log to file
        log_file_name = f"purged_messages_{interaction.channel.id}.txt"
        with open(log_file_name, "w", encoding="utf-8") as f:
            f.write(log_content)

        # Send log file to log_channel
        await log_channel(
            title="Purged Messages",
            description=f"Purged `{len(deleted)}` messages from {interaction.channel.mention} by {interaction.user.mention}",
            color=discord.Color.random(),
            guild=interaction.guild,
            file=discord.File(log_file_name)
        )

        # Clean up by removing the file from the local system after sending
        os.remove(log_file_name)

        # Send confirmation to the interaction channel
        await interaction.followup.send(f"Deleted {len(deleted)} messages.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))