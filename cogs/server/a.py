import discord
import random
from discord.ext import commands
from utils.other.a import *

class A(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ns(self, ctx: commands.Context, category: str = None):
        channel = discord.utils.get(ctx.guild.channels, name="ee")
        if category is None:
            category = random.choice(types)

        url = await nS(category)
    
        if url:
            await channel.send(url)

        else:
            await ctx.send("Err")

async def setup(bot: commands.Bot):
    await bot.add_cog(A(bot))