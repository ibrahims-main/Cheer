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
        self.db = sqlite3.connect("utils/database/warns.db")
        self.cur = self.db.cursor()
        self.setup_db()

    def setup_db(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS warns (
                        memid INTEGER,
                        reason TEXT,
                        mod INTEGER,
                        time INTEGER,
                        wid TEXT
                    )""")
        self.db.commit()

    def get_wid(self):
        wid = "#"
        ink = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

        while True:
            # Generate a random 5-character wid
            wid += ''.join(choice(ink) for _ in range(5))

            # Check if the generated wid already exists in the database
            cur = self.cur.execute("SELECT wid FROM warns WHERE wid = ?", (wid,))
            res = cur.fetchone()

            # If the fetched result is None, it means the wid is unique
            if res is None:
                break
            else:
                # Reset wid for the next iteration
                wid = "#"

        return wid

    @app_commands.command(name="warn", description="Warn a member")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, *, reason: str):
        wid = self.get_wid()  # Changed to synchronous
        await self.cur.execute("INSERT INTO warns VALUES(?,?,?,?,?)", (member.id, reason, interaction.user.id, int(time()), wid,))
        self.db.commit()

        description = f"✔ Warned: `{str(member)}` Reason: `{reason}`"
        color = discord.Color.random()

        await interaction.response.send_message(
            embed=discord.Embed(
                description=description,
                color=color
            )
        )

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
    @commands.has_permissions(manage_guild=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        cur = self.cur.execute("SELECT * FROM warns WHERE memid = ? ORDER BY time DESC", (member.id,))
        res = cur.fetchall()

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
            description=f"{member.mention} warnings:", color=discord.Color.red())
        wc = 1
        for i in res:
            embed.add_field(
                name=f"Warn {wc}:",
                value=f"**Warned by:** <@{i[2]}> **for:** {i[1]} **on:** <t:{i[3]}:R> **Id:** `{i[4]}`",
                inline=False)
            wc += 1

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarnings", description="Clear a member's warnings")
    @commands.has_permissions(manage_guild=True)
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member):
        try:
            self.cur.execute("DELETE FROM warns WHERE memid=?", (member.id,))
            self.db.commit()
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

        except Exception as e:
            await interaction.response.send_message("OOPS, an error occurred while clearing warnings.")

    @app_commands.command(name="delete-warn", description="Delete a member's warning")
    @commands.has_permissions(manage_guild=True)
    async def delete_warn(self, interaction: discord.Interaction, warn_id: str):
        try:
            self.cur.execute("DELETE FROM warns WHERE wid=?", (warn_id,))
            self.db.commit()
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

        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"No warnings found with id: **{warn_id}**",
                    color=discord.Color.red())
                )

    async def cog_unload(self):
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))