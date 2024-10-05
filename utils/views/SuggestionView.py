import discord 
from discord.ui import Modal, TextInput

class SuggestionModal(Modal):
    def __init__(self):
        super().__init__(title="Submit Suggestion")

        self.add_item(TextInput(label="Your Suggestion", style=discord.TextStyle.long))
        

    async def on_submit(self, interaction: discord.Interaction):
        suggestion = self.children[0].value
        embed = discord.Embed(title="User Suggestion", color=discord.Color.blue())
        embed.add_field(name="User", value=interaction.user.mention, inline=False)
        embed.add_field(name="Suggestion", value=suggestion, inline=False)
        embed.set_footer(
            text="Suggestion ID: {0}".format(interaction.message.id)
        )

        suggestion_channel = interaction.guild.get_channel(1289977074081071124)

        message = await suggestion_channel.send(embed=embed)

        await message.add_reaction("✅")
        await message.add_reaction("❌")

        await interaction.response.send_message("Your suggestion has been submitted!", ephemeral=True)