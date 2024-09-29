import discord
import time
import os
import asyncio
import chat_exporter
from dotenv import load_dotenv
from discord.ui import Button, View
from github import Github
from os import getenv

load_dotenv()
GTOKEN = getenv("GTOKEN")

async def get_transcript(member: discord.Member, channel: discord.TextChannel):
    export = await chat_exporter.export(channel=channel)
    file_name=f"{member.id}.html"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(export)

def upload(file_path: str, member_name: str):
    github = Github(GTOKEN)
    repo = github.get_repo("ibrahims-main/tickets")
    file_name = f"{int(time.time())}"
    repo.create_file(
        path=f"tickets/{file_name}.html",
        message="Ticket Log for {0}".format(member_name),
        branch="main",
        content=open(f"{file_path}","r",encoding="utf-8").read()
    )
    os.remove(file_path)

    return file_name

async def send_log(title: str, guild: discord.Guild, description: str, color: discord.Color):
    log_channel = guild.get_channel(1289953695424843776)
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    await log_channel.send(embed=embed)

class CreateButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, emoji="🎫", custom_id="ticketopen")
    async def ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, id=1289957925393137726)
        for ch in category.text_channels:
            if ch.topic == f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL!":
                await interaction.followup.send("You already have a ticket in {0}".format(ch.mention), ephemeral=True)
                return
            
        r1: discord.Role = interaction.guild.get_role(1281221303474327603)
        r2: discord.Role = interaction.guild.get_role(1281221291403247758)
        r3: discord.Role = interaction.guild.get_role(1281221288844857427)
        r4: discord.Role = interaction.guild.get_role(1281221281760677908)
        r5: discord.Role = interaction.guild.get_role(1281215207779074068)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r2: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r3: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r4: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r5: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await category.create_text_channel(
            name=str(interaction.user),
            topic=f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL!",
            overwrites=overwrites
        )
        await channel.send(
            embed=discord.Embed(
                title="Ticket Created!",
                description="Dont ping the staff member, they will be here soon",
                color=discord.Color.random()
            ),
            view=CloseButton()
        )
        await interaction.followup.send(
            embed = discord.Embed(
                description="Created your ticket at {0}".format(channel.mention),
                color=discord.Color.blurple()
            ),
            ephemeral=True
        )

        await send_log(
            title="Ticket Created",
            description="Created by {0}".format(interaction.user.mention),
            color=discord.Color.random(),
            guild=interaction.guild
        )

class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="closeticket")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        await interaction.channel.send("Closing the ticket in 3 seconds!...")
        await asyncio.sleep(3)

        category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, id=1289957925393137726)
        r1: discord.Role = interaction.guild.get_role(1281221303474327603)
        r2: discord.Role = interaction.guild.get_role(1281221291403247758)
        r3: discord.Role = interaction.guild.get_role(1281221288844857427)
        r4: discord.Role = interaction.guild.get_role(1281221281760677908)
        r5: discord.Role = interaction.guild.get_role(1281215207779074068)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await interaction.channel.edit(category=category, overwrites=overwrites)
        await interaction.channel.send(
            embed = discord.Embed(
                description="Ticket Closed!",
                color=discord.Color.red()
            ),
            view=TrashButton()
        )

        member = interaction.guild.get_member(int(interaction.channel.topic.split(" ")[0]))
        await get_transcript(member=member, channel=interaction.channel)
        file_name = upload(f"{member.id}.html", member.name)
        link = f"https://ibrahims-main.github.io/tickets/tickets/{file_name}"
        await send_log(
            title="Ticket Closed",
            description=f"Closed by: {interaction.user.mention}\n[click for transcript]({link})",
            color=discord.Color.yellow(),
            guild=interaction.guild
        )

class TrashButton(View):
    def __init__(self):
        super().__init__(timeout=None)

        @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.red, emoji="🚮", custom_id="trash")
        async def trash(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer()
            await interaction.channel.send("Deleting the ticket in 3 seconds")
            await asyncio.sleep(3)
            await interaction.channel.delete()

            await send_log(
                title="Ticket Deleted",
                description=f"Deleted by {interaction.user.mention}, ticket: {interaction.channel.name}",
                color=discord.Color.red(),
                guild=interaction.guild
            )