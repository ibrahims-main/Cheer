import discord
import sqlite3
from discord.ext import commands
from discord import app_commands
from typing import Coroutine, Optional
from easy_pil import Editor, load_image_async, Font

level = ["Bleh (5)", "YEAH (15)", "Daddy (25)", "MY MANN (50)"]
level_num = [5, 15, 25, 50]

class Leveling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/levels.db")
        self.cur = self.db.cursor()
        self.setup_db()

    def setup_db(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        """)
        self.db.commit()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.content.startswith(":)") and not message.author.bot:

            self.cur.execute("SELECT * FROM user_levels WHERE user_id = ?", (message.author.id,))
            user_data = self.cur.fetchone()

            if user_data:

                xp = user_data[1]
                lvl = user_data[2]
                increased_xp = xp + 25
                new_level = increased_xp // 100

                self.cur.execute("UPDATE user_levels SET xp = ? WHERE user_id = ?", (increased_xp, message.author.id,))
                self.db.commit()

                if new_level > lvl:

                    await message.channel.send(message.author.mention, embed = discord.Embed(
                        title="Get a life",
                        description=f"Nah my man {message.author.mention} just levelled up to {new_level}! Bro get a life",
                        color=discord.Color.random()
                    ))

                    self.cur.execute("UPDATE user_levels SET level = ?, xp = ? WHERE user_id = ?", (new_level, 0, message.author.id,))
                    self.db.commit()

                    for i in range(len(level)):

                        if new_level == level_num[i]:
                            await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level[i]))

                            embed = discord.Embed(
                                title="LESSSS GOOO!",
                                description=f"MY MAN {message.author.mention} JUST GOT THE **{level[i]}** ROLE!",
                                color=discord.Color.random()
                            )
                            embed.set_thumbnail(url=message.author.avatar.url)

                            await message.channel.send(message.author.mention, embed=embed)
                
            else:

                self.cur.execute("INSERT INTO user_levels (user_id) VALUES (?)", (message.author.id,))
                self.db.commit()

    @app_commands.command(name="rank", description="display yours or someone else's level")
    async def rank(self, interaction: discord.Interaction, user: Optional[discord.Member]):
        userr = user or interaction.user

        self.cur.execute("SELECT * FROM user_levels WHERE user_id = ?", (userr.id,))
        user_data = self.cur.fetchone()

        if user_data:

            xp = user_data[1]
            lvl = user_data[2]
            next_level_xp = (lvl + 1) * 100
            xp_need = next_level_xp
            xp_have = xp

            percentage = int(((xp_have * 100) / xp_need)) if xp_need > 0 else 0

            background = Editor("utils/imgs/zIMAGE.jpg")
            profile = await load_image_async(str(userr.avatar.url))
            profile = Editor(profile).resize((150, 150)).circle_image()

            poppins = Font.poppins(size=40)
            poppins_small = Font.poppins(size=30)
            ima = Editor("utils/imgs/zBLACK.png")
            background.paste(profile.image, (30, 30))

            background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
            background.bar((30, 220), max_width=650, height=40, percentage=percentage, fill="#ff9933", radius=20)
            background.text((200, 40), str(userr.name), font=poppins, color="#ff9933")
            background.rectangle((200, 100), width=350, height=2, fill="#ff9933")
            background.text((200, 130), f"Level: {lvl}   XP: {xp} / {next_level_xp}", font=poppins_small, color="#ff9933")

            card = discord.File(fp=background.image_bytes, filename="zCARD.png")
            await interaction.response.send_message(file=card)

    @app_commands.command(name="leaderboard", description="Displays the server's leaderboard")
    async def leaderboard(self, interaction: discord.Interaction, amount: int = 5):
        self.cur.execute("SELECT user_id, xp, level FROM user_levels")
        data = self.cur.fetchall()

        l = {}
        total_xp = []

        for user_id, xp, lvl in data:
            total_xp_value = int(xp + (lvl * 100))
            l[total_xp_value] = (user_id, lvl, xp)
            total_xp.append(total_xp_value)

        total_xp.sort(reverse=True)
        index = 1

        embed = discord.Embed(
            title="This Servers Non-Grass Touchers",
            color=discord.Color.random()
        )

        for amt in total_xp:
            user_id, lvl, xp = l[amt]
            member = await self.bot.fetch_user(user_id)

            if member is not None:
                embed.add_field(name=f"{index}. {member.name}", value=f"**Level: {lvl} | XP: {xp}**", inline=False)
                if index == amount:
                    break
                index += 1

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank_reset", description="Resets a user's rank")
    async def rank_reset(self, interaction: discord.Interaction, user: Optional[discord.Member]):
        member = user or interaction.user

        if member != interaction.user:
            role1 = discord.utils.get(interaction.guild.roles, name="Supreme Mod Overlord")
            role2 = discord.utils.get(interaction.guild.roles, name="God-Mode Guardian")
            role3 = discord.utils.get(interaction.guild.roles, name=":)")
            if not role1 or not role2 or not role3 in member.roles:
                await interaction.response.send_message(f"You can only reset your data; to reset other data, you must have {role1.mention}, {role2.mention} or {role3.mention} roles",  ephemeral=True)
                return
            
        self.cur.execute("DELETE FROM user_levels WHERE user_id = ?", (member.id,))
        self.db.commit()

        await interaction.response.send_message(embed=discord.Embed(title="OOF Rank Reset!", description=f"{member.mention} rank got reset", color=discord.Color.random()))

    @app_commands.command(name="increase_level", description="Increase a users level")        
    async def increase_level(self, interaction: discord.Interaction, increase_by: int, user: Optional[discord.Member]):
        member = user or interaction.user

        role1 = discord.utils.get(interaction.guild.roles, name="Supreme Mod Overlord")
        role2 = discord.utils.get(interaction.guild.roles, name="God-Mode Guardian")
        role3 = discord.utils.get(interaction.guild.roles, name=":)")
        if not role1 or not role2 or not role3 in member.roles:
            await interaction.response.send_message(f"NAHH LOOK AT BRO; ONLY THESE ROLES CAN INCREASE LEVEL {role1.mention}, {role2.mention} or {role3.mention}",  ephemeral=True)
            return
            
        self.cur.execute("UPDATE user_levels SET level = level + ? WHERE user_id = ?", (increase_by, member.id))
        self.db.commit()

        await interaction.response.send_message(embed=discord.Embed(title="Level Increased!", description=f"{member.mention} level increased by {increase_by} wow good for my man", color=discord.Color.random()))

    @app_commands.command(name="increase_xp", description="increase a users xp")
    async def increase_xp(self, interaction: discord.Interaction, increase_by: int, user: Optional[discord.Member]):
        member = user or interaction.user

        role1 = discord.utils.get(interaction.guild.roles, name="Supreme Mod Overlord")
        role2 = discord.utils.get(interaction.guild.roles, name="God-Mode Guardian")
        role3 = discord.utils.get(interaction.guild.roles, name=":)")
        if not role1 or not role2 or not role3 in member.roles:
            await interaction.response.send_message(f"NAHH LOOK AT BRO; ONLY THESE ROLES CAN INCREASE LEVEL {role1.mention}, {role2.mention} or {role3.mention}",  ephemeral=True)
            return
        
        self.cur.execute("UPDATE user_levels SET xp = xp + ? WHERE user_id = ?", (increase_by, member.id))
        self.db.commit()

        await interaction.response.send_message(embed=discord.Embed(title="XP Increased!", description=f"{member.mention} XP increased by {increase_by} wow good for my man", color=discord.Color.random()))

    def cog_unload(self):
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Leveling(bot))