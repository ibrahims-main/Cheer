import discord
from discord.ext import commands
from discord import app_commands

class ModLogCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="modlog", description="View a member's modlog")
    @app_commands.checks.has_permissions(kick_members=True)
    async def modlog(self, interaction: discord.Interaction, member: discord.Member):
        modlog_cog = self.bot.get_cog("Modlog")

        if not modlog_cog:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description="Modlog cog not found.",
                    color=discord.Color.red()
                )
            )
        
        cur = modlog_cog.cur.execute("SELECT * FROM modlog WHERE user_id=?", (member.id,))
        logs = cur.fetchall()

        if not logs:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title=" ",
                    description=f"{member.display_name} has no moderation logs.",
                    color=discord.Color.red()
                )
            )
        
        embed = discord.Embed(
            title=f"{member.display_name}'s Moderation Logs",
            description=" ",
            color=discord.Color.blue()
        )

        for log in logs:
            timestamp = log[3]
            action = log[1]
            reason = log[2]
            moderator_id = log[4]
            moderator = self.bot.get_user(moderator_id)

            embed.add_field(
                name=f"{action} at <t:{timestamp}:R>",
                value=f"Reason: {reason}\nModerator: {moderator.mention if moderator else 'Unknown'}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModLogCommand(bot))