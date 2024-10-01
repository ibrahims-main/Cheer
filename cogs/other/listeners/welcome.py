import discord
from discord import app_commands
from discord.ext import commands
from easy_pil import Editor, load_image_async, Font
from utils.other.log_channel import log_channel

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel

        background = Editor("utils/imgs/welcome.jpg")
        profile_image = await load_image_async(str(member.avatar.url))

        profile = Editor(profile_image).resize((150, 150)).circle_image()
        poppins = Font.poppins(size=50, variant="bold")

        poppins_small = Font.poppins(size=20, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

        background.text((400, 260), f"WELCOME TO {member.guild.name}", color="white", font=poppins, align="center")
        background.text((400, 325), f"{member.name}#{member.discriminator}", color="white", font=poppins_small, align="center")

        file = discord.File(fp=background.image_bytes, filename="utils/imgs/welcome.jpg")
        await channel.send(f"{member.mention} WELCOME TO :) | Hope you love your stay <3")
        await channel.send(file=file)

        log_channel(
            title="Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green(),
            guild=member.guild,
            file=file
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))