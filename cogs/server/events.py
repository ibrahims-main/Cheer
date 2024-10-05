import discord
import sqlite3
from discord.ext import commands
from discord import app_commands

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/events.db")
        self.cur = self.db.cursor()
        self.events_channel_id = 1292097836258689086
        self.events_vc_id = 1292098720204324974
        self.setup_db()

    def setup_db(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                date TEXT,
                time TEXT,
                organizer_id INTEGER
            )
        """)
        self.db.commit()

    @app_commands.command(name="event", description="Create a new event")
    @app_commands.checks.has_permissions(administrator=True)
    async def event(self, interaction: discord.Interaction, title: str, description: str, date: str, time: str):
        self.cur.execute(
            "INSERT INTO events (title, description, date, time, organizer_id) VALUES (?,?,?,?,?)",
            (title, description, date, time, interaction.user.id)
        )
        self.db.commit()

        channel = self.bot.get_channel(self.events_channel_id)
        role = discord.utils.get(interaction.guild.roles, name="Game Night Ping")
        if channel:
            await channel.send(
                f"{role.mention}",
                embed=discord.Embed(
                    title="GAMEEE NIGHTT!",
                    description=f"**Event:** {title}\n**Description:** {description}\n**Date:** {date}\n**Time:** {time}\n\nJoin THE EVENTS VC quickly!",
                    color=discord.Color.green()
                )
            )

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Event Created",
                description=f"Event '{title}' has been created!",
                color=discord.Color.green()
            )
        )

    @app_commands.command(name="join_event", description="Join the event voice channel")
    async def join_event(self, interaction: discord.Interaction):
        """Moves the user to the event voice channel if there's an active event."""
        # Check if there are any events in the database
        self.cur.execute("SELECT * FROM events")
        events = self.cur.fetchall()

        if not events:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="There are no active events. You cannot join the voice channel.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
        
        voice_channel = self.bot.get_channel(self.events_vc_id)
        if isinstance(voice_channel, discord.VoiceChannel):
            if interaction.user.voice:
                await interaction.user.move_to(voice_channel)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"You have joined the event voice channel: {voice_channel.name}",
                        color=discord.Color.green()
                    )
                )
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        description="You need to be in a voice channel to join the event.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="The event voice channel does not exist.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @app_commands.command(name="leave_event", description="Leave the event voice channel")
    async def leave_event(self, interaction: discord.Interaction):
        """Moves the user out of the event voice channel."""
        if interaction.user.voice:
            await interaction.user.move_to(None)
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="You have left the event voice channel.",
                    color=discord.Color.green()
                )
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="You are not in a voice channel.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @app_commands.command(name="list_events", description="List all upcoming events")
    async def list_events(self, interaction: discord.Interaction):
        """List all upcoming events."""
        self.cur.execute("SELECT * FROM events")
        events = self.cur.fetchall()

        if not events:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description="No upcoming events found.",
                    color=discord.Color.red()
                )
            )

        embed = discord.Embed(title="Upcoming Events", color=discord.Color.blue())
        for event in events:
            embed.add_field(
                name=event[1],  # Event title
                value=f"Description: {event[2]}\nDate: {event[3]}\nTime: {event[4]}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    def cog_unload(self):
        self.db.close()