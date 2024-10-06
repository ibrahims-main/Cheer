import discord
import sqlite3
import time
from pytimeparse import parse
from random import choice
from discord.ext import commands, tasks
from discord import app_commands

class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/reminders.db")
        self.cur = self.db.cursor()
        self.setup_db()
        self.reminder_task.start()

    def setup_db(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS reminder (
                user_id INTEGER,
                message TEXT,
                time INTEGER,
                channel_id INTEGER,
                reminder_id TEXT
            )
        """)
        self.db.commit()

    def create_reminder_id(self) -> str:
        """Generates a unique reminder ID."""
        ink = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        attempts = 0
        max_attempts = 100  # Limit attempts to avoid infinite loops
        while attempts < max_attempts:
            wid = "#" + ''.join(choice(ink) for _ in range(5))
            cur = self.cur.execute("SELECT reminder_id FROM reminder WHERE reminder_id=?", (wid,))
            res = cur.fetchone()
            if res is None:
                return wid
            attempts += 1
        raise Exception("Could not generate a unique reminder ID after several attempts.")


    def convert_time(self, times: str) -> int:
        """Converts a time string to seconds using pytimeparse."""
        return parse(times)

    @app_commands.command(name="remind", description="Set a reminder.")
    async def remind(self, interaction: discord.Interaction, times: str, message: str):
        time_in_sec = self.convert_time(times)

        if not time_in_sec:
            return await interaction.response.send_message(
                "Invalid time format. Please use formats like '10m', '2h', etc.",
                ephemeral=True
            )

        epoch = time_in_sec + int(time.time())
        reminder_id = self.create_reminder_id()

        # Insert reminder into the database
        self.cur.execute(
            "INSERT INTO reminder (user_id, message, time, channel_id, reminder_id) VALUES (?, ?, ?, ?, ?)",
            (interaction.user.id, message, epoch, interaction.channel.id, reminder_id)
        )
        self.db.commit()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Reminder Set!",
                description=f"I'll remind you <t:{epoch}:R> for: **{message}**",
                color=discord.Color.random()
            ),
            ephemeral=True
        )

    @app_commands.command(name="reminders", description="List all your reminders.")
    async def reminders(self, interaction: discord.Interaction):
        cur = self.cur.execute("SELECT * FROM reminder WHERE user_id=?", (interaction.user.id,))
        reminders = cur.fetchall()

        if not reminders:
            return await interaction.response.send_message("You don't have any reminders set.", ephemeral=True)

        embed = discord.Embed(title="Your Reminders", color=discord.Color.random())
        for reminder in reminders:
            embed.add_field(
                name=f"Reminder ID: {reminder[4]}",
                value=f"Message: {reminder[1]} - Time: <t:{reminder[2]}:R>",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="delete_reminder", description="Delete a reminder by its ID.")
    async def delete_reminder(self, interaction: discord.Interaction, reminder_id: str):
        cur = self.cur.execute("SELECT * FROM reminder WHERE user_id=? AND reminder_id=?", (
            interaction.user.id, reminder_id))
        reminder = cur.fetchone()

        if not reminder:
            return await interaction.response.send_message("No reminder found with that ID.", ephemeral=True)

        self.cur.execute("DELETE FROM reminder WHERE user_id=? AND reminder_id=?", (
            interaction.user.id, reminder_id))
        self.db.commit()

        await interaction.response.send_message(f"Deleted reminder: **{reminder[1]}**", ephemeral=True)

    @app_commands.command(name="clear_reminders", description="Clear all your reminders.")
    async def clear_reminders(self, interaction: discord.Interaction):
        self.cur.execute("DELETE FROM reminder WHERE user_id=?", (interaction.user.id,))
        self.db.commit()
        await interaction.response.send_message("All your reminders have been cleared.", ephemeral=True)

    @tasks.loop(seconds=10)
    async def reminder_task(self):
        cur = self.cur.execute("SELECT * FROM reminder WHERE time<=?", (int(time.time()),))
        reminders = cur.fetchall()

        for reminder in reminders:
            user = self.bot.get_user(reminder[0])

            if user is None:
                continue  # Skip if user is not found

            try:
                await user.send(f"Reminder: **{reminder[1]}**")
            except discord.Forbidden:
                channel = self.bot.get_channel(reminder[3])
                if channel:
                    await channel.send(f"{user.mention}, Reminder: **{reminder[1]}**")

            # Delete reminder after sending
            self.cur.execute("DELETE FROM reminder WHERE reminder_id=?", (reminder[4],))
        
        self.db.commit()

    def cog_unload(self):
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))