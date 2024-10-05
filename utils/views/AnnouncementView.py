import discord
from discord.ui import Modal, TextInput

class AnnouncementModal(Modal):
    def __init__(self):
        super().__init__(title="Announcement")

        self.add_item(TextInput(label="Announcement", style = discord.TextStyle.long))

    async def on_submit(self, interaction: discord.Interaction):
        announcement = self.children[0].value
        embed = discord.Embed(
            title="NEW ANNOUNCEMENT",
            description=announcement,
            color=discord.Color.random()
        )
        embed.set_footer(text=f"by: {interaction.user.name}")

        channel = discord.utils.get(interaction.guild.channels, id=1290668027460980768)

        await channel.send(embed=embed)

        await interaction.response.send_message(
            "Announcement send!",
            ephemeral=True
        )