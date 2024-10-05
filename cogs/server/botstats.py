import discord
import psutil
from discord.ext import commands
from discord import app_commands

class BotStats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_cpu_usage(self):

        return psutil.cpu_percent()
    
    def get_ram_usage(self):
        used =  psutil.virtual_memory().used // 1048576 
        total = psutil.virtual_memory().total // 1048576

        return f"{round(used)}MB / {round(total)}MB"

    def get_disk_usage(self):
        used = psutil.disk_usage('/').used // 1073741824
        total = psutil.disk_usage('/').total // 1073741824

        return f"{round(used, 2)}GB / {round(total, 2)}GB"

    def get_ram_usage_percent(self):

        return psutil.virtual_memory().percent

    def get_disk_usage_percent(self):

        return psutil.disk_usage('/').percent
        
    def get_python_version(self):

        return "3.11.1"

    def get_discord_version(self):

        return "2.0.0b7"
    
    @app_commands.command(name="botstats", description="Displays the Bots Statistics")
    @app_commands.checks.has_permissions(administrator=True)
    async def botstats(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Stats", color=discord.Color.green())

        embed.add_field(name="CPU Usage", value=f"```{self.get_cpu_usage()}%```", inline=False)
        embed.add_field(name="Memory Usage", value=f"```{self.get_ram_usage_percent()}%```", inline=False)
        embed.add_field(name="Disk Usage", value=f"```{self.get_disk_usage_percent()}%```", inline=False)
        embed.add_field(name="Python Version", value=f"```{self.get_python_version()}```", inline=False)
        embed.add_field(name="Discord Version", value=f"```{self.get_discord_version()}```", inline=False)
        embed.add_field(name="Latency", value=f"```{round(self.bot.latency * 1000)}ms```", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(BotStats(bot))