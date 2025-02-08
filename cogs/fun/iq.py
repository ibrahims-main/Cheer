import discord
import random
from discord.ext import commands
from discord import app_commands

class Iq(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="iq", description="Generate a random IQ score!")
    async def iq(self, interaction: discord.Interaction, user: discord.Member):
        iq_score = random.randint(50, 200)
        levels = [
            "🧑‍🌾 **Farmer Brain** 🐄",
            "🤓 **Average Thinker** 🤔",
            "🧠 **Big Brain Mode** 🧠",
            "🟣 **Genius Alert!** 💡",
            "🚀 **Next-Level Einstein!** 🌌"
        ]
        level = levels[min((iq_score - 50) // 40, 4)]
        embed = discord.Embed(
            title="🧠 IQ Test Results 🧠",
            description=f"{user.mention} has an IQ of **{iq_score}!**\n{level}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Iq(bot))