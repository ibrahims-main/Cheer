import discord
import time
import sqlite3
from random import choice
from discord.ext import commands

class Automod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/warns.db")
        self.cur = self.db.cursor()
        
    def get_wid(self):
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
    
    def get_banned_words(self):
        with open("utils/other/banned_words.txt") as f:
            words = f.read().split(", ")
        return words
    
    def get_new_message(self, message: discord.Message):
        sentence = message.content
        banned_words = self.get_banned_words()
        found_words = []
        for word in banned_words:
            if word in sentence.lower():
                sentence = sentence.replace(word, "*" * len(word))
                found_words.append(word)
        found_words = ", ".join(found_words)
        return sentence, found_words
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return
        try:
            if message.guild and (message.author.guild_permissions.administrator or message.author.bot):
                return
        except:
            pass
        new_message = self.get_new_message(message)
        if not new_message[0] == message.content:
            await message.delete()
            embeds = [
                discord.Embed(description=f"{message.author.mention} used a banned word!", color=discord.Color.brand_red()),
                discord.Embed(description=f"{new_message[0]}", color=discord.Color.dark_orange())
            ]
            await message.channel.send(embeds=embeds)
            reason = f"Banned word(s) used: '{new_message[1]}'"
            wid = self.get_wid()  # Removed `await` because `get_wid` is synchronous
            self.cur.execute("INSERT INTO warns VALUES(?, ?, ?, ?, ?)", (message.author.id, reason, self.bot.user.id, int(time.time()), wid))
            self.db.commit()
            try:
                await message.author.send(embed=discord.Embed(description=f"You were warned for: {reason}", color=discord.Color.dark_purple()))
            except discord.Forbidden:
                pass

    async def cog_unload(self):
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Automod(bot))