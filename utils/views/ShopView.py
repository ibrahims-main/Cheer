import discord
from typing import List, Tuple

class ShopView(discord.ui.View):
    def __init__(self, page: int, total_items: int, items: List[Tuple[str, int]], cog):
        super().__init__()
        self.page = page
        self.total_items = total_items
        self.items = items
        self.cog = cog
        self.ITEMS_PER_PAGE = 10

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.page > 1:
            self.page -= 1
            await self.send_shop_page(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.page * self.ITEMS_PER_PAGE < self.total_items:
            self.page += 1
            await self.send_shop_page(interaction)

    async def send_shop_page(self, interaction: discord.Interaction):
        await self.cog.send_shop_page(interaction, self.page)