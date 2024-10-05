import discord
from discord import app_commands
from discord.ext import commands

class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rules", description="Displays the server rules.")
    async def rules(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="RULES!",
            description="*which yall better follow",
            color=discord.Color.random()
        )

        embed.add_field(
            value="",
            name="* Respect everyone",
            inline=False
        )
        embed.add_field(
            value="",
            name="* No spam or self-promotion (server invites, advertisements etc) without permission from a staff member. This includes DMing fellow members. Only Bots are allowed with permission of moderator :)",
            inline=False
        )
        embed.add_field(
            value="",
            name="No age-restricted or obscene content. This includes text, images or links featuring nudity, sex, hard violence or other disturbing graphic content.",
            inline=False
        )
        embed.add_field(
            value="",
            name="If you see something against the rules or something that makes you feel unsafe, let staff know. We want this server to be a welcoming space!",
            inline=False
        )
        embed.add_field(
            value="",
            name="Casual swearing is allowed, But No Excessive Vulgarity",
            inline=False
        )
        embed.add_field(
            value="",
            name="No Harassment or Bullying",
            inline=False
        )
        embed.add_field(
            value="",
            name="Follow Discord's Terms of Service",
            inline=False
        )
        embed.add_field(
            value="",
            name="have fun :)",
            inline=False
        )

        embed.set_thumbnail(url=interaction.guild.icon.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rules(bot))