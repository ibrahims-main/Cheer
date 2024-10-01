import discord
from discord.ext import commands
from discord import app_commands
from utils.other.log_channel import log_channel

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="kick a dumbo from the party (bleh).")
    @commands.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, * , reason: str):
        await member.kick(reason=reason)
        title = "KICKED! BOOM!"
        description = "Dumbo by the name {0} HAS BEEN KICKED by {1}".format(member.mention, interaction.user.mention)
        color = discord.Color.random()

        await interaction.response.send_message(
            embed=discord.Embed(
                title=title,
                description=description,
                color=color
            )
        )

        await log_channel(
            title=title,
            description=description,
            color=color,
            guild=interaction.guild
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Kick(bot))