import discord
from discord.ext import commands

class MessageListeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        log_channel = discord.utils.get(before.guild.channels, id=1290309804513820725)

        if before.content != after.content:
            embed = discord.Embed(
                title="Message Edited",
                description=f"A message was edited in {before.channel.mention}.",
                color=discord.Color.blue(),
                timestamp=after.created_at,
            )
            embed.add_field(name="Before", value=before.content or "No content", inline=False)
            embed.add_field(name="After", value=after.content or "No content", inline=False)
            embed.set_author(name=str(after.author), icon_url=after.author.avatar.url)
            embed.set_footer(text=f"Message ID: {after.id}")

            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        
        log_channel = discord.utils.get(message.guild.channels, id=1290309804513820725)

        embed = discord.Embed(
            title="Message Deleted",
            description=f"A message was deleted in {message.channel.mention}.",
            color=discord.Color.red(),
            timestamp=message.created_at,
        )
        embed.add_field(name="Content", value=message.content or "No content", inline=False)
        embed.set_author(name=str(message.author), icon_url=message.author.avatar.url)
        embed.set_footer(text=f"Message ID: {message.id}")

        await log_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageListeners(bot))