import discord
import aiohttp
from discord import app_commands
from discord.ext import commands

class Joke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Tells a joke.")
    async def joke(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://v2.jokeapi.dev/joke/Any") as response:
                if response.status == 200:
                    data = await response.json()

                    if data["type"] == "single":
                        joke = data["joke"]
                        await interaction.response.send_message(embed=discord.Embed(
                            description=joke
                        ))
                    else:
                        setup = data["setup"]
                        delivery = data["delivery"]
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{setup}\n{delivery}"
                            )
                        )
                else:
                    await interaction.response.send_message("Could not fetch a joke at this time. Please try again later!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Joke(bot))