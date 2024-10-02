import discord
from discord import app_commands
from discord.ext import commands
from utils.other.timeConverter import TimeConverter
from utils.other.log_channel import log_channel

class Slowmode(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="sets the slowmode for dumb people who talk fast")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, *, time: str):
        # Use the TimeConverter to convert the time argument
        try:
            time = await TimeConverter().convert(interaction, time)
        except commands.BadArgument as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error!",
                    description=str(e),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        # Set slowmode delay in the channel
        await interaction.channel.edit(slowmode_delay=int(time))

        await interaction.response.send_message(f"✅ Slowmode has been set to {int(time)} seconds.")

        await log_channel(
            guild=interaction.guild,
            title="Slowmode activated!",
            description=f"✅ Slowmode has been set to {int(time)} seconds in channel: {interaction.channel.mention} by {interaction.user.mention}",
            color=discord.Color.random()
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Slowmode(bot))