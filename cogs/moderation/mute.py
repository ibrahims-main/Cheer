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

    @app_commands.command(name="mute", description="Mute a Dumbo :)")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, *, time: TimeConverter):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted:)")
        
        # Collect the member's roles (excluding the @everyone role) and store them
        original_roles = [role for role in member.roles if role != interaction.guild.default_role]
        muted_members[member.id] = original_roles

        # Remove all roles and assign the Muted role
        await member.remove_roles(*original_roles)
        await member.add_roles(muted_role)

        title = "Muted!"
        description = f"MUTED {member.mention} for {time} seconds HAHA by {interaction.user.mention}"
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

        # Wait for the duration of the mute, then unmute the member
        await asyncio.sleep(time)

        await self.unmute(interaction.guild, member, muted_role)

    @app_commands.command(name="unmute", description="Unmute a Dumbo :)")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted:)")

        # Check if the member has the muted role
        if muted_role not in member.roles:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error!",
                    description=f"{member.mention} is not muted.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        # Remove the Muted role
        await member.remove_roles(muted_role)

        # Restore the original roles, if they were stored
        if member.id in muted_members:
            await member.add_roles(*muted_members[member.id])
            del muted_members[member.id]

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Unmuted!",
                description=f"{member.mention} has been unmuted.",
                color=discord.Color.green()
            )
        )

        await log_channel(
            title="Unmuted!",
            description=f"{member.mention} has been unmuted.",
            color=discord.Color.green(),
            guild=interaction.guild
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Mute(bot))