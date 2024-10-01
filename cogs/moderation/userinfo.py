import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone

class UserInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="user_info", description="Displays information about a user.")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        user = member or interaction.user

        roles = [role.mention for role in member.roles[1:]]
        roles = roles if roles else ["None"]

        embed = discord.Embed(
            title=f"User Info - {member.mention}",
            color=discord.Color.random(),
            timestamp=datetime.now(timezone.utc)
        )

        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick if member.nick else "None", inline=True)
        embed.add_field(name="Bot", value=member.bot, inline=True)

        # Account and server information
        embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=True)
        
        # Status and roles
        embed.add_field(name="Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="Activity", value=member.activity.name if member.activity else "None", inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles), inline=False)

        # Display user's profile and banner (if they have one)
        if member.banner:
            embed.set_image(url=member.banner.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(UserInfo(bot))