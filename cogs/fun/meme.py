import discord
import aiohttp
from discord import app_commands
from discord.ext import commands

class Meme(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="meme", description="Sends a random meme")
    async def meme(self, interaction:discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as response:
                if response.status == 200:
                    data = await response.json()
                    meme_url = data["url"]
                    meme_title = data["title"]
                    meme_subreddit = data["subreddit"]

                    embed = discord.Embed(
                        title=meme_title,
                        description=f"From: r/{meme_subreddit}",
                        color=discord.Color.random()
                    )
                    embed.set_image(url=meme_url)

                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Could not fetch a meme at this time. Please try again later!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Meme(bot))