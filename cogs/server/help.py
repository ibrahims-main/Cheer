import discord
from discord.ext import commands
from discord import app_commands
from ezpage import PaginationEmbedView # Personally made library for paginations

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays the bot's commands.")
    async def help(self, interaction: discord.Interaction):
        embeds = []
        total_pages = 5  # Number of pages

        # 🌟 Fun Commands
        embed1 = discord.Embed(title="🎉 Fun Commands", description="Enjoy some fun and interactive commands!", color=0x3498db)
        embed1.add_field(name="🎱 **/8ball**", value="Ask the magic 8-ball a question!", inline=False)
        embed1.add_field(name="😂 **/joke**", value="Get a random joke.", inline=False)
        embed1.add_field(name="📷 **/meme**", value="Fetch a random meme.", inline=False)
        embed1.add_field(name="✌ **/rps**", value="Play rock-paper-scissors against the bot.", inline=False)
        embed1.add_field(name="🎲 **/dice**", value="Rolls a six-sided die.", inline=False)
        embed1.add_field(name="💘 **/pickup**", value="Get a random pickup line to impress someone!", inline=False)
        embed1.add_field(name="💘 **/simprate**", value="Check how much of a simp someone is!", inline=False)
        embed1.add_field(name="💘 **/ship**", value="Rate the relationship compatibility between two users! (Cheer never lies)", inline=False)
        embed1.add_field(name="🏳️‍🌈 **/gayrate**", value="See how 'gay' someone is! (Just for fun)", inline=False)
        embed1.add_field(name="🤓 **/iq**", value="Generate a random IQ score!", inline=False)
        embed1.set_footer(text=f"Page 1 of {total_pages} | Requested by {interaction.user.name}")
        embeds.append(embed1)

        # 📈 Leveling System Commands
        embed2 = discord.Embed(title="📈 Leveling System Commands", description="Track your rank and XP.", color=0x2ecc71)
        embed2.add_field(name="🏆 **/rank**", value="Check your current rank and XP.", inline=False)
        embed2.add_field(name="📊 **/leaderboard**", value="View the server's leaderboard.", inline=False)
        embed2.add_field(name="🔄 **/rank_reset (Admin Only To Reset Someone Elses)**", value="Reset your rank or **@admin** for others.", inline=False)
        embed2.add_field(name="📈 **/increase_level  (Admin Only)**", value="Increase a user's level manually.", inline=False)
        embed2.add_field(name="✨ **/increase_xp  (Admin Only)**", value="Increase XP for a user manually.", inline=False)
        embed2.set_footer(text=f"Page 2 of {total_pages} | Requested by {interaction.user.name}")
        embeds.append(embed2)

        # ⚔️ Moderation Commands
        embed3 = discord.Embed(title="⚔️ Moderation Commands", description="Commands for server moderation. **(Admin Only)**", color=0xe67e22)
        embed3.add_field(name="🔨 **/ban**", value="Ban a user from the server.", inline=False)
        embed3.add_field(name="👢 **/kick**", value="Kick a user from the server.", inline=False)
        embed3.add_field(name="🔒 **/lockdown**", value="Locks the current channel.", inline=False)
        embed3.add_field(name="📜 **/modlog**", value="View moderation logs.", inline=False)
        embed3.add_field(name="🔇 **/mute**", value="Mute a user.", inline=False)
        embed3.add_field(name="📛 **/warn**", value="Warn a user.", inline=False)
        embed3.add_field(name="🗑 **/purge**", value="Delete multiple messages at once.", inline=False)
        embed3.add_field(name="💬 **/revive**", value="Boost server activity (every 4 hours).", inline=False)
        embed3.add_field(name="⏳ **/slowmode**", value="Set slow mode for a channel.", inline=False)
        embed3.add_field(name="🔓 **/unlock**", value="Unlock a channel.", inline=False)
        embed3.add_field(name="🎟️ **:)ticketview**", value="", inline=False)
        embed3.set_footer(text=f"Page 3 of {total_pages} | Requested by {interaction.user.name}")
        embeds.append(embed3)

        # 🌍 Server Commands
        embed4 = discord.Embed(title="🌍 Server Commands", description="Server-related commands.", color=0x1abc9c)
        embed4.add_field(name="🛑 **/afk**", value="Set yourself as AFK.", inline=False)
        embed4.add_field(name="📢 **/announce**", value="Make an announcement.", inline=False)
        embed4.add_field(name="🎂 **/birthday**", value="Set your birthday (`YYYY-MM-DD`).", inline=False)
        embed4.add_field(name="📊 **/botstats**", value="Check bot stats.", inline=False)
        embed4.add_field(name="📆 **/event**", value="Create a new event.", inline=False)
        embed4.add_field(name="📝 **/join_event**", value="Join an event.", inline=False)
        embed4.add_field(name="🚪 **/leave_event**", value="Leave an event.", inline=False)
        embed4.add_field(name="📜 **/list_events**", value="List all server events.", inline=False)
        embed5.set_footer(text=f"Page 4 of {total_pages} | Requested by {interaction.user.name}")
        embeds.append(embed4)

        embed5 = discord.Embed(title="", description="", color=0x1abc9c)
        embed5.add_field(name="📌 **/help**", value="Show help menu.", inline=False)
        embed5.add_field(name="⏰ **/remind**", value="Set a reminder.", inline=False)
        embed5.add_field(name="📋 **/reminders**", value="View all your reminders.", inline=False)
        embed5.add_field(name="🗑 **/delete_reminder**", value="Delete a specific reminder.", inline=False)
        embed5.add_field(name="🚮 **/clear_reminders**", value="Clear all reminders.", inline=False)
        embed5.add_field(name="📖 **/rules**", value="View server rules.", inline=False)
        embed5.add_field(name="💡 **/suggest**", value="Suggest a new feature or improvement.", inline=False)
        embed5.add_field(name="🆔 **/user_info**", value="View user info.", inline=False)
        embed5.set_footer(text=f"Page 5 of {total_pages} | Requested by {interaction.user.name}")
        embeds.append(embed5)

        view = PaginationEmbedView(embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))