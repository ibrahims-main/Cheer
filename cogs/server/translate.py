import discord
from discord import app_commands
from discord.ext import commands
from googletrans import Translator, LANGUAGES

class Translate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.translator = Translator()

    @app_commands.command(name="translate", description="Translate text to another language.")
    async def translate(self, interaction: discord.Interaction, text: str, target_language: str):
        target_language = target_language.lower()

        if target_language not in LANGUAGES:
            await interaction.response.send_message(
                f"❌ Invalid language code! Use a valid ISO 639-1 code.\nExample: `en` (English), `fr` (French), `es` (Spanish).",
                ephemeral=True
            )
            return

        try:
            translation = self.translator.translate(text, dest=target_language)
            embed = discord.Embed(title="🌍 Translation", color=discord.Color.blue())
            embed.add_field(name="📜 Original", value=text, inline=False)
            embed.add_field(name=f"🗣️ Translated ({LANGUAGES[target_language].capitalize()})", value=translation.text, inline=False)
            embed.set_footer(text=f"Requested by {interaction.user.name}")

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Translation failed! Error: `{e}`", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Translate(bot))