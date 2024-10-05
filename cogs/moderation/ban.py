import discord
from discord.ext import commands
from discord import app_commands
from utils.other.log_channel import log_channel

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a dumbo from the party.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, * , reason: str):
        await member.ban(reason=reason)
        title = "BANNED! BOOM!"
        description = "Dumbo by the name {0} HAS BEEN BANNED by {1}".format(member.mention, interaction.user.mention)
        color = discord.Color.random()

        await interaction.response.send_message(
            embed=discord.Embed(
                title=title,
                description=description,
                color=color
            )
        )

        modlog_cog = self.bot.get_cog("ModLog")
        if modlog_cog:
            modlog_cog.log_action(member.id, "Ban", reason, interaction.user.id)

        await log_channel(
            title=title,
            description=description,
            color=color,
            guild=interaction.guild
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))