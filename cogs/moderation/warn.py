import discord
import sqlite3
from random import choice
from utils.other.log_channel import log_channel
from time import time
from discord.ext import commands
from discord import app_commands

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/warns.db", detect_types=sqlite3.PARSE_DECLTYPES)
        self.cur = self.db.cursor()
        self.setup_db()

    def setup_db(self):
        """Initializes the database table for warnings."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                memid INTEGER,
                reason TEXT,
                mod INTEGER,
                time INTEGER,
                wid TEXT
            )
        """)
        self.db.commit()

    def get_wid(self):
        """Generates a unique warning ID."""
        wid = "#"
        ink = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

        while True:
            wid += ''.join(choice(ink) for _ in range(5))
            cur = self.cur.execute("SELECT wid FROM warns WHERE wid = ?", (wid,))
            res = cur.fetchone()
            if res is None:
                break
            else:
                wid = "#"

        return wid

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, *, reason: str):
        """Warns a member and logs it in the database."""
        try:
            wid = self.get_wid()
            self.cur.execute(
                "INSERT INTO warns (memid, reason, mod, time, wid) VALUES (?, ?, ?, ?, ?)",
                (member.id, reason, interaction.user.id, int(time()), wid)
            )
            self.db.commit()
        except sqlite3.Error as e:
            await interaction.response.send_message(f"Error saving the warning: {str(e)}", ephemeral=True)
            return

        description = f"✔ Warned: `{str(member)}` Reason: `{reason}`"
        color = discord.Color.random()

        await interaction.response.send_message(
            embed=discord.Embed(
                description=description,
                color=color
            )
        )

        modlog_cog = self.bot.get_cog("ModLog")
        if modlog_cog:
            modlog_cog.log_action(member.id, "Warn", reason, interaction.user.id, wid)

        try:
            await member.send(
                embed=discord.Embed(
                    description=f"You have been warned in {interaction.guild.name} for `{reason}`",
                    color=color
                )
            )
        except discord.Forbidden:
            pass  # Ignore if the member can't be DMed

        await log_channel(
            description=description,
            title="Member Warned",
            guild=interaction.guild,
            color=color,
        )

    @app_commands.command(name="warnings", description="Check a member's warnings")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Lists all warnings of a specific member."""
        try:
            cur = self.cur.execute("SELECT * FROM warns WHERE memid = ? ORDER BY time DESC", (member.id,))
            res = cur.fetchall()
        except sqlite3.Error as e:
            await interaction.response.send_message(f"Database error: {str(e)}", ephemeral=True)
            return

        color = discord.Color.random()
        if not res:
            description = f"<:cross:966707196396814366> {str(member)} has no warnings :("
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=description,
                    color=color
                )
            )

        embed = discord.Embed(
            description=f"{member.mention}'s warnings:", color=discord.Color.red())
        wc = 1
        for i in res:
            embed.add_field(
                name=f"Warn {wc}:",
                value=f"**Warned by:** <@{i[2]}> **for:** {i[1]} **on:** <t:{i[3]}:R> **Id:** `{i[4]}`",
                inline=False)
            wc += 1

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarnings", description="Clear a member's warnings")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member):
        """Clears all warnings of a specific member and deletes associated mod logs."""
        try:
            self.cur.execute("DELETE FROM warns WHERE memid = ?", (member.id,))
            self.db.commit()

            # Get ModLog cog and delete associated mod logs
            modlog_cog = self.bot.get_cog("ModLog")
            if modlog_cog:
                modlog_cog.clear_logs_for_member(member.id, "Warn")
        except sqlite3.Error as e:
            await interaction.response.send_message(f"Error clearing warnings: {str(e)}", ephemeral=True)
            return

        title = "Warnings Cleared"
        description = f"<:tick:966707201064464395> {str(member)}'s warnings cleared successfully!"
        color = discord.Color.random()

        await interaction.response.send_message(
            embed=discord.Embed(
                title=title,
                description=description,
                color=color
            )
        )

        await log_channel(
            title=title,
            description=description,
            guild=interaction.guild,
            color=color,
        )

    @app_commands.command(name="delete-warn", description="Delete a member's warning")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def delete_warn(self, interaction: discord.Interaction, warn_id: str):
        """Deletes a specific warning by its ID and removes the associated mod log."""
        try:
            cur = self.cur.execute("DELETE FROM warns WHERE wid = ?", (warn_id,))
            if cur.rowcount == 0:
                raise ValueError("No warnings found with that ID.")
            self.db.commit()

            # Get ModLog cog and delete associated mod log
            modlog_cog = self.bot.get_cog("ModLog")
            if modlog_cog:
                modlog_cog.delete_log_by_warning_id(warn_id)
        except (sqlite3.Error, ValueError) as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"No warnings found with id: **{warn_id}**",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        title = "Warning Deleted"
        description = f"<:tick:966707201064464395> Warning with id `{warn_id}` deleted successfully!"
        color = discord.Color.random()

        await interaction.response.send_message(
            embed=discord.Embed(
                title=title,
                description=description,
                color=color
            )
        )

        await log_channel(
            title=title,
            description=description,
            guild=interaction.guild,
            color=color,
        )

    async def cog_unload(self):
        """Closes the database connection when the cog is unloaded."""
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))