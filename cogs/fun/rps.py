import discord
import random
from discord.ext import commands
from discord import app_commands

class RPS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rps", description="Play rock-paper-scissors against the bot.")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        if choice.lower() not in choices:
            await interaction.response.send_message("Invalid choice! Please choose rock, paper, or scissors.")
            return
        
        if choice.lower() == bot_choice.lower():
            await interaction.response.send_message(f"You chose {choice}, and the bot chose {bot_choice}. It's a tie!")

        elif (choice.lower() == "rock" and bot_choice.lower() == "scissors") or \
             (choice.lower() == "paper" and bot_choice.lower() == "rock") or \
             (choice.lower() == "scissors" and bot_choice.lower() == "paper"):
            await interaction.response.send_message(f"You chose {choice}, and the bot chose {bot_choice}. You win!")

        else:
            await interaction.response.send_message(f"You chose {choice}, and the bot chose {bot_choice}. You lose!")

async def setup(bot: commands.Bot):
    await bot.add_cog(RPS(bot))