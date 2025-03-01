import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

FFMPEG_OPTIONS = {
    "options": "-vn"
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    async def search_song(self, query: str):
        """Search YouTube and return the first video URL"""
        ydl_opts = {"format": "bestaudio", "noplaylist": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info["entries"]:
                return info["entries"][0]["url"]
        return None

    @app_commands.command(name="play", description="🎵 Play a song from YouTube")
    async def play(self, interaction: discord.Interaction, query: str):
        """Plays a song from YouTube"""
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ You must be in a voice channel.", ephemeral=True)
        
        voice_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client or await voice_channel.connect()
        
        url = await self.search_song(query)
        if not url:
            return await interaction.response.send_message("❌ No results found.", ephemeral=True)

        if interaction.guild.id not in self.queue:
            self.queue[interaction.guild.id] = []
        self.queue[interaction.guild.id].append(url)

        await interaction.response.send_message(f"🎶 Added to queue: `{query}`")

        if not vc.is_playing():
            await self.play_next(interaction)

    async def play_next(self, interaction):
        """Plays the next song in the queue"""
        if self.queue[interaction.guild.id]:
            url = self.queue[interaction.guild.id].pop(0)
            vc = interaction.guild.voice_client
            vc.stop()
            vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop))
            await interaction.followup.send(f"🎵 Now playing: `{url}`")

    @app_commands.command(name="pause", description="⏸ Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        """Pauses the current song"""
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸ Music paused.")

    @app_commands.command(name="resume", description="▶️ Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        """Resumes paused music"""
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Resumed playing.")

    @app_commands.command(name="skip", description="⏭ Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        """Skips the current song"""
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭ Skipped!")
            await self.play_next(interaction)

    @app_commands.command(name="stop", description="⏹ Stop the music and leave the voice channel")
    async def stop(self, interaction: discord.Interaction):
        """Stops the music and disconnects the bot"""
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            self.queue[interaction.guild.id] = []
            await interaction.response.send_message("⏹ Stopped music and left the voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))