import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class EightBall(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question.")
    async def eight_ball(self, interaction: discord.Interaction, *, question: str):
        async with aiohttp.ClientSession() as session:
            # Using the 8ball API for a random response
            async with session.get("https://8ball.developers.workers.dev/") as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data["answer"]

                    # Send the response back to the user
                    await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {answer}")
                else:
                    await interaction.response.send_message("Could not fetch a response from the magic 8-ball. Please try again later!")

async def setup(bot: commands.Bot):
    await bot.add_cog(EightBall(bot))