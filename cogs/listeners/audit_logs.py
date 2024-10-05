import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from os import getenv
import aiohttp

load_dotenv()

class AuditLogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.webhook_url = getenv("WEBHOOK_URL")
        self.log_channel_id = 1290309804513820725 
        self.last_audit_id = None 
        self.session = None

        # Start the audit log monitoring loop
        self.monitor_audit_logs.start()

    # This function sends a message to the webhook with the audit log details
    async def send_webhook_log(self, entry: discord.AuditLogEntry):
        action_map = {
            discord.AuditLogAction.ban: "🚫 Ban",
            discord.AuditLogAction.unban: "🔓 Unban",
            discord.AuditLogAction.kick: "👢 Kick",
            discord.AuditLogAction.member_update: "🔄 Member Update",
            discord.AuditLogAction.role_create: "✨ Role Created",
            discord.AuditLogAction.role_delete: "🗑️ Role Deleted",
            discord.AuditLogAction.channel_create: "📁 Channel Created",
            discord.AuditLogAction.channel_delete: "🗑️ Channel Deleted",
            discord.AuditLogAction.emoji_create: "🤤 Emoji Created",
            discord.AuditLogAction.emoji_delete: "🗑️ Emoji Deleted",
            discord.AuditLogAction.overwrite_create: "🎀 Overwrite Created",
            discord.AuditLogAction.overwrite_delete: "🗑️ Overwrite Deleted",
            discord.AuditLogAction.overwrite_update: "Overwrite Updated",
            discord.AuditLogAction.invite_create: "🔥 Invite Created",
            discord.AuditLogAction.invite_delete: "😒 Invite Deleted",
            discord.AuditLogAction.message_pin: "⛏ Message Pinned",
            discord.AuditLogAction.guild_update: "✔ Guild Update",
            discord.AuditLogAction.thread_create: "🧣 Thread Created",
            discord.AuditLogAction.thread_delete: "🗑️ Thread Deleted",
        }

        action_title = action_map.get(entry.action, "⚙️ Action Detected")

        embed = discord.Embed(
        title=f"{action_title}",
        color=discord.Color.random(),
        description=f"**Target:** {entry.target}\n"
                    f"**Performed By:** {entry.user.mention} ({entry.user})\n"
                    f"**Reason:** {entry.reason or 'No reason provided'}",
        timestamp=entry.created_at
    )

        embed.set_footer(text="Audit Log", icon_url=self.bot.user.avatar.url)
        embed.set_author(name="Audit Log Entry", icon_url=self.bot.user.avatar.url)

        # Add an optional field for more details
        embed.add_field(name="Details", value=f"**Entry ID:** {entry.id}\n**Action Type:** {entry.action}", inline=False)

        if self.session is None:
            print("Session not initialized.")
            return

        async with self.session.post(self.webhook_url, json={
            "embeds": [embed.to_dict()]
        }) as response:
            if response.status != 204:
                print(f"Failed to send webhook log with status code: {response.status}")

    @tasks.loop(seconds=10)
    async def monitor_audit_logs(self):
        for guild in self.bot.guilds:
            try:
                async for entry in guild.audit_logs(limit=5, oldest_first=False):
                    if self.last_audit_id is None or entry.id > self.last_audit_id:
                        await self.send_webhook_log(entry)
                        self.last_audit_id = entry.id
            except discord.Forbidden:
                print(f"Missing permissions to view the audit log in {guild.name}")

    @monitor_audit_logs.before_loop
    async def before_monitor_audit_logs(self):
        await self.bot.wait_until_ready()

        if self.session is None:
            self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.monitor_audit_logs.cancel() 

        if self.session and not self.session.closed:
            self.bot.loop.create_task(self.session.close())

async def setup(bot: commands.Bot):
    await bot.add_cog(AuditLogs(bot))