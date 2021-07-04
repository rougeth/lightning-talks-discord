import re
import typing
from collections import defaultdict
from dataclasses import dataclass, field

import discord
from discord.ext import commands
from discord.ext.tasks import loop
from jinja2 import Template
from decouple import config

import templates
import db


DISCORD_TOKEN = config("DISCORD_TOKEN")
CATEGORY_NAME = "Palestras Relâmpago"
CHANNEL_NAME = "quero-participar"


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


def render(template, **kwargs):
    t = Template(template)
    content = t.render(**kwargs)
    return "**[beta]**\n\n" + content


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


@pr.command(name="iniciar")
async def init(ctx, *args):
    lt = await db.check_active_lightning_talk(ctx.guild.id)
    if lt:
        await ctx.message.add_reaction("❌")
        await ctx.channel.send("There is an active lightning talk!")
        return

    channel = await get_or_create_lightning_talk_channel(ctx.guild)
    message = await channel.send(render(templates.NEW_LIGHTNING_TALK))
    await db.create_lightning_talk(ctx.guild.id, message.id)
    await ctx.message.add_reaction("✅")


@pr.command(name="encerrar")
async def close(ctx, *args):
    lt = await db.check_active_lightning_talk(ctx.guild.id)
    if not lt or not lt["open_registration"]:
        await ctx.message.add_reaction("❌")
        await ctx.channel.send("There is no lightning talk in progress or open for registration!")
        return

    await db.close_lightning_talk(lt["guild_id"], lt["message_id"])

    message = await ctx.fetch_message(lt["message_id"])
    await message.edit(content=render(templates.NOT_ACTIVE_LIGHTNING_TALK))

    await ctx.message.add_reaction("✅")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
