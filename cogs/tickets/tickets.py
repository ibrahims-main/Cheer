import discord
from discord.ext import commands
from utils.views.TicketView import CreateButton

class TicketSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command(name="ticketview")
    @commands.has_permissions(administrator=True)
    async def ticketview(self, ctx: commands.Context):
        await ctx.send(
            embed=discord.Embed(
                description="Press the button to create a new ticket"
            ),
            view=CreateButton()
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketSystem(bot))