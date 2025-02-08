import discord
import random
from discord import app_commands
from discord.ext import commands

class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ship", description="Rate the relationship compatibility between two users!")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        # Generate a random compatibility score
        ship_percent = random.randint(0, 100)

        # Heart progress bar
        hearts_full = "❤️" * (ship_percent // 10)
        hearts_empty = "💔" * ((100 - ship_percent) // 10)
        progress_bar = f"{hearts_full}{hearts_empty}"

        # Relationship level descriptions
        levels = [
            "💀 **Not Meant to Be...** (RIP 💔)",
            "😐 **Friendzone...** (Ouch 🫠)",
            "😏 **There's a Spark!** (Maybe? 👀)",
            "😍 **Power Couple!** (🔥🔥🔥)",
            "💘 **SOULMATES!** (Wedding Bells? 💍)"
        ]
        level = levels[min(ship_percent // 25, 4)]

        # Create an embed message
        embed = discord.Embed(
            title="💖 Love Compatibility Test 💖",
            description=f"{user1.mention} 💞 {user2.mention}\n\n"
                        f"**Compatibility Score:** **{ship_percent}%**\n\n"
                        f"{progress_bar}\n\n"
                        f"{level}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Powered by Love AI™ ❤️")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ship(bot))