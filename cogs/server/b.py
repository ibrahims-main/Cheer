import discord
import aiohttp
from discord.ext import commands

class B(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def r34(self, ctx: commands.Context, *, tag: str = None):
        if not tag:
            return await ctx.send("Please provide a search term!")
        
        url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}"
        channel = discord.utils.get(ctx.guild.channels, name="ee")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send("Couldn't fetch. Try again later.")
                    return

                data = await response.json()

                if len(data) == 0:
                    await ctx.send(f"No results found for tag: {tag}")
                    return
                
                # Get a random post from the result
                random_post = data[0]
                image_url = random_post['file_url']

                # Send the image URL to the user
                await channel.send(f"{image_url}")

async def setup(bot: commands.Bot):
    await bot.add_cog(B(bot))