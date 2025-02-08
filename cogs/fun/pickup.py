import discord
import aiohttp
from discord import app_commands
from discord.ext import commands

class Pickup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pickup", description="Get a random pickup line to impress someone!")
    async def pickup(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://rizzapi.vercel.app/random") as response:
                if response.status == 200:
                    data = await response.json()
                    pickup_line = data.get("text", "Couldn't fetch a pickup line! Try again later.")
                else:
                    pickup_line = "Oops! Failed to fetch a pickup line."

        embed = discord.Embed(title="💘 Pickup Line Generator", description=pickup_line, color=discord.Color.pink())
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Pickup(bot))