import discord
from discord.ext import commands

class SuggestionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return  # Ignore bot reactions

        message = reaction.message
        if not message.embeds:
            return  # Only handle messages with embeds (suggestions)

        embed = message.embeds[0]
        suggestion_author = embed.fields[0].value  # User mention stored in the embed

        # Get the specific role (:) role in this case)
        role = discord.utils.get(user.guild.roles, name=":)")

        # Check if the user has the required role
        if role in user.roles:
            if reaction.emoji == "✅":
                # Approve the suggestion
                await message.channel.send(embed=discord.Embed(
                    description=f"Suggestion by the id {message.id} has been approved by {user.mention}!"))
                # Optionally notify the author of the suggestion
                await message.add_reaction("👍")
            elif reaction.emoji == "❌":
                # Disapprove the suggestion
                await message.channel.send(embed=discord.Embed(
                    description=f"Suggestion by the id {message.id} has been disapproved by {user.mention}!"
                ))
                # Optionally notify the author of the suggestion
                await message.add_reaction("👎")

async def setup(bot: commands.Bot):
    await bot.add_cog(SuggestionCog(bot))