import discord
import random
import time
import sqlite3
from discord.ext import commands
from discord import app_commands

class Afk(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/afk.db")
        self.cur = self.db.cursor()
        self.setup_db()

    def setup_db(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS afk (memid INTEGER, memname TEXT, memres TEXT, afktime INTEGER)')
        self.db.commit()

    @app_commands.command(name="afk", description="Sets your AFK")
    async def afk(self, interaction: discord.Interaction, reason: str = None):
        reason = reason or "AFK"
        member = interaction.user
        cur = self.cur.execute("SELECT memres FROM afk WHERE memid=?", (member.id,))
        res = cur.fetchone()

        if not res:
            self.cur.execute("INSERT INTO afk (memid, memname, memres, afktime) VALUES (?, ?, ?, ?)",
                             (member.id, member.display_name, reason, int(time.time())))
            self.db.commit()

            try:
                await member.edit(nick=f"[AFK] {member.display_name}")
            except discord.Forbidden:
                pass  # Handle lack of permissions gracefully

            emoji = random.choice(['⚪', '🔴', '🟤', '🟣', '🟢', '🟡', '🟠', '🔵'])
            embed = discord.Embed(
                description=f"{emoji} I set your AFK: {reason}",
                color=discord.Color.random()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                description="You are already AFK",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener(name="on_message")
    async def check_afk(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        if message.guild.id == 1281201986779217990:
            # Check for AFK status
            cur = self.cur.execute("SELECT memname, afktime FROM afk WHERE memid=?", (message.author.id,))
            res = cur.fetchone()
            if res:
                afktime = res[1]
                tp = int(time.time()) - afktime
                if tp >= 30:  # AFK duration threshold
                    self.cur.execute("DELETE FROM afk WHERE memid=?", (message.author.id,))
                    self.db.commit()
                    try:
                        await message.author.edit(nick=res[0])
                    except discord.Forbidden:
                        pass  # Handle lack of permissions gracefully

                    embed = discord.Embed(
                        description="I removed your AFK",
                        color=discord.Color.random()
                    )
                    await message.reply(embed=embed)

            # Check mentions for AFK
            for mention in message.mentions:
                cur = self.cur.execute("SELECT memres, afktime FROM afk WHERE memid=?", (mention.id,))
                res = cur.fetchone()
                if res:
                    embed = discord.Embed(
                        description=f"{mention.mention} is AFK: {res[0]} (Last seen: <t:{res[1]}:>)",
                        color=discord.Color.random()
                    )
                    await message.reply(embed=embed)
                    break  # Only respond to the first mention

    def cog_unload(self):
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Afk(bot))