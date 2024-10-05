import discord
import time

class CooldownHandler:
    def __init__(self):
        self.cooldowns = {}

    def is_on_cooldown(self, user_id: int, cooldown: int):
        current_time = time.time()
        if user_id in self.cooldowns:
            last_used = self.cooldowns[user_id]
            if current_time - last_used < cooldown:
                return True, cooldown - (current_time - last_used)
        return False, 0
    
    def update_cooldown(self, user_id: int):
        self.cooldowns[user_id] = time.time()

cooldown_handler = CooldownHandler()

def cooldown_check(cooldown_time: int):
    async def predicate(interaction: discord.Interaction):
        is_cooldown, remaining_time = cooldown_handler.is_on_cooldown(interaction.user.id, cooldown_time)
        if is_cooldown:
            embed = discord.Embed(
                title="Error!",
                description=f"You are on cooldown. Please wait {int(remaining_time)} seconds.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        cooldown_handler.update_cooldown(interaction.user.id)
        return True
    
    return discord.app_commands.check(predicate)