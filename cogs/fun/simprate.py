import discord
import random
from discord import app_commands
from discord.ext import commands

class SimpRate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="simprate", description="Check how much of a simp someone is!")
    async def simprate(self, interaction: discord.Interaction, user: discord.Member):
        rate = random.randint(0, 100)
        levels = [
            "✅ **Certified Anti-Simp** 😎",
            "🔹 **Slight Simp Tendencies** 🤔",
            "💙 **Casual Simp** 😏",
            "❤️ **Big-Time Simp!** 🥰",
            "💘 **Ultimate Simp Overlord!** 🤡"
        ]
        level = levels[min(rate // 25, 4)]
        embed = discord.Embed(
            title="💖 Simp Meter 💖",
            description=f"{user.mention} is **{rate}%** a simp!\n{level}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SimpRate(bot))