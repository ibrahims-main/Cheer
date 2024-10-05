import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from utils.other.timeConverter import TimeConverter
from utils.other.log_channel import log_channel

# Dictionary to store muted members and their roles
muted_members = {}

class Mute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Mute a member for a certain time")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, time: str, *, reason: str = "No reason provided"):
        # Use the TimeConverter to convert the time argument
        try:
            time_seconds = await TimeConverter().convert(interaction, time)  # Time is already in seconds
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

        # Get or create the Muted:) role
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted:)")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted:)", reason="For muting members")

        # Collect the member's roles (excluding @everyone) and store them
        original_roles = [role for role in member.roles if role != interaction.guild.default_role]
        muted_members[member.id] = original_roles

        # Remove all roles and assign the Muted:) role
        await member.remove_roles(*original_roles)
        await member.add_roles(muted_role)

        title = "Muted!"
        description = f"{member.mention} was muted for {time_seconds} seconds by {interaction.user.mention}\nReason: {reason}"
        color = discord.Color.random()

        await interaction.response.send_message(
            embed=discord.Embed(
                title=title,
                description=description,
                color=color
            )
        )

        # Log the mute action in ModLog
        modlog_cog = self.bot.get_cog("ModLog")
        if modlog_cog:
            modlog_cog.log_action(member.id, "Mute", reason, interaction.user.id)

        # Send the log to the log channel
        await log_channel(
            title=title,
            description=description,
            color=color,
            guild=interaction.guild
        )

        # Wait for the duration of the mute, then unmute the member
        await asyncio.sleep(time_seconds)
        await self.unmute_(interaction.guild, member, muted_role)

    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        # Unmute the member through the command
        await self.unmute_(interaction.guild, member)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Unmuted!",
                description=f"{member.mention} has been unmuted.",
                color=discord.Color.green()
            )
        )

    async def unmute_(self, guild: discord.Guild, member: discord.Member, muted_role=None):
        # If muted_role is not passed, retrieve it
        if not muted_role:
            muted_role = discord.utils.get(guild.roles, name="Muted:)")

        # Check if the member has the muted role
        if muted_role not in member.roles:
            return

        # Remove the Muted:) role
        await member.remove_roles(muted_role)

        # Restore the original roles, if they were stored
        if member.id in muted_members:
            try:
                await member.add_roles(*muted_members[member.id])
                del muted_members[member.id]
            except discord.Forbidden:
                print(f"Failed to restore roles for {member.mention}. Missing permissions.")

        # Log the unmute action to the log channel
        await log_channel(
            title="Unmuted!",
            description=f"{member.mention} has been unmuted.",
            color=discord.Color.green(),
            guild=guild
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Mute(bot))