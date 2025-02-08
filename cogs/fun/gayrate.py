import discord
import random
from discord.ext import commands
from discord import app_commands

class GayRate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="gayrate", description="See how 'gay' someone is! (Just for fun)")
    async def gayrate(self, interaction: discord.Interaction, user: discord.Member):
        rate = random.randint(0, 100)
        levels = [
            "🏳️‍🌈 **Totally Straight** 😐",
            "🌈 **Bi-curious** 🤨",
            "💅 **A little fruity** 🍉",
            "💖 **Certified Gay!** 💖",
            "🏳️‍🌈 **Rainbow Supreme Overlord!** 🌟"
        ]
        level = levels[min(rate // 25, 4)]
        embed = discord.Embed(
            title="🏳️‍🌈 Gay Rate Scanner 🌈",
            description=f"{user.mention} is **{rate}%** gay!\n{level}",
            color=discord.Color.magenta()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(GayRate(bot))