import discord
from discord.ext import commands
from discord import app_commands

class Nickname(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="nick", description="Change a users nickname")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(self, interaction: discord.Interaction, member: discord.Member, *, new_nickname: str):
        try:
            await member.edit(nick=new_nickname)
            await interaction.response.send_message(f"Nickname changed successfully for {member.mention}")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have the permission to change the nickname.")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"An error occurred: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Nickname(bot))