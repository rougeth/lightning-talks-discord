import re
import typing
from collections import defaultdict
from dataclasses import dataclass, field

import discord
from discord.ext import commands
from discord.ext.tasks import loop

from decouple import config


DISCORD_TOKEN = config("DISCORD_TOKEN")
CATEGORY_NAME = "Palestras Relâmpago"
CHANNEL_NAME = "quero-participar"


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


async def get_or_create_lightning_talk_channel(guild: discord.Guild):
    channels = await guild.fetch_channels()
    category = discord.utils.get(
        channels, name=CATEGORY_NAME, type=discord.ChannelType.category
    )
    if not category:
        category = await guild.create_category(CATEGORY_NAME)

    channel = discord.utils.get(category.text_channels, name=CHANNEL_NAME)
    if not channel:
        await category.create_text_channel(CHANNEL_NAME)

    return channel


@bot.group(invoke_without_command=True)
async def pr(ctx, *args):
    await ctx.channel.send("TODO: help")


@pr.command()
async def build(ctx, *args):
    await get_or_create_lightning_talk_channel(ctx.guild)
    await ctx.message.add_reaction("✅")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
