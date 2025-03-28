import discord
from discord import app_commands
from discord.ext import commands
from utils.other.log_channel import log_channel

class Unban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="unban", description="Unban a dumbo.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, *, user: discord.User, reason: str = "None"):
        guild = interaction.guild

        try:
            await guild.unban(user, reason)
            title = "UNBANNED!"
            description = f"User: {user} has been unbanned by {interaction.user.mention} for Reason: {reason}"

            await interaction.response.send_message(
                embed=discord.Embed(
                    title=title,
                    description=description,
                    color=discord.Color.random()
                )
            )

            modlog_cog = self.bot.get_cog("ModLog")
            if modlog_cog:
                modlog_cog.log_action(user.id, "Unban", reason, interaction.user.id)

            await log_channel(
                guild=interaction.guild,
                title=title,
                description=description,
                color=discord.Color.green()
            )

        except discord.NotFound:
            await interaction.response.send_message("User not found or not banned")
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to unban the user.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))