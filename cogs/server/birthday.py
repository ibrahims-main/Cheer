import discord
import datetime
import sqlite3
from discord.ext import commands, tasks
from discord import app_commands

class Birthday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/birthdays.db")
        self.cur = self.db.cursor()
        self.setup_db()
        self.check_birthdays.start()

    def setup_db(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS birthdays (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                date TEXT
            )
        """)
        self.db.commit()

    @app_commands.command(name="birthday", description="Add your birthday")
    async def birthday(self, interaction: discord.Interaction, date: str):
        try:
            birthday_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if birthday_date < datetime.date.today():
                await interaction.response.send_message(
                    embed=discord.Embed(
                        description="You cannot add a birthday in the past.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Invalid date format. Use YYYY-MM-DD.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
        
        self.cur.execute(
            "INSERT INTO birthdays (user_id, date) VALUES (?, ?)",
            (interaction.user.id, birthday_date.strftime("%Y-%m-%d"),)
        )
        self.db.commit()

        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"Your birthday has been set to {birthday_date}.",
                color=discord.Color.green()
            )
        )

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.cur.execute("SELECT user_id FROM birthdays WHERE date =?", (today,))
        birthdays_today = self.cur.fetchall()

        if birthdays_today:
            guild = discord.utils.get(self.bot.guilds)
            birthday_role = discord.utils.get(guild.roles, name="Birthday Ping")

            for (user_id,) in birthdays_today:
                user = guild.get_member(user_id)
                if user:
                    channel = discord.utils.get(guild.text_channels, name="birthdays")  # Specify your channel name
                    if channel:
                        await channel.send(f"{birthday_role.mention}\nHAPPPPPPY BIRTHDAYYY TO {user.mention}!")

    def cog_unload(self):
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Birthday(bot))