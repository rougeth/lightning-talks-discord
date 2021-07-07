import re
import typing
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import shuffle

import discord
from discord.ext import commands
from discord.ext.tasks import loop
from jinja2 import Template
from decouple import config
from loguru import logger

import templates
import db


DISCORD_TOKEN = config("DISCORD_TOKEN")
CATEGORY_NAME = "Palestras Relâmpago"
CHANNEL_NAME = "quero-participar"
ORG_CHANNEL_NAME = "org-only"

JOIN_QUEUE_EMOJI = "☝️"


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


def lt_not_in_progress(ctx, lt):
    if not all(
        [
            lt,
            lt.get("message_id") != ctx.message.id,
            lt.get("in_progress"),
        ]
    ):
        raise Exception("Não encontrei nenhuma palestra relâmpago iniciada")


def lt_open_registration(ctx, lt):
    if lt.get("open_registration"):
        raise Exception("Inscrições estão abertas")


def lt_speakers_defined(ctx, lt):
    if lt.get("speakers"):
        raise Exception("Lista de palestrantes já foi definida")


def fail_command_on(*functions):
    def decorator(f):
        async def wrapper(ctx, *args, **kwargs):
            lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
            for check in functions:
                try:
                    check(ctx, lt)
                except Exception as e:
                    await ctx.message.add_reaction("❌")
                    await ctx.channel.send(str(e))
                    return
            return await f(ctx, *args, **kwargs)

        return wrapper

    return decorator


def render(template, **kwargs):
    t = Template(template)
    content = t.render(**kwargs)
    return "**[beta]**\n" + content


async def get_or_create_lightning_talk_channel(
    guild: discord.Guild, org_role: discord.Role
):
    channels = await guild.fetch_channels()
    category = discord.utils.get(
        channels, name=CATEGORY_NAME, type=discord.ChannelType.category
    )
    if not category:
        category = await guild.create_category(CATEGORY_NAME)

    permissions_all = discord.PermissionOverwrite.from_pair(
        discord.Permissions.all(), []
    )

    channel = discord.utils.get(category.text_channels, name=CHANNEL_NAME)
    if not channel:
        logger.debug(f"Creating main channel. name={CHANNEL_NAME!r}")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: permissions_all,
        }
        channel = await category.create_text_channel(
            CHANNEL_NAME, overwrites=overwrites
        )

    return channel


@bot.group(invoke_without_command=True)
async def pr(ctx, *args):
    await ctx.channel.send("TODO: help")


@pr.command()
async def build(ctx, org_role: discord.Role, *args):
    await get_or_create_lightning_talk_channel(ctx.guild, org_role)
    await ctx.message.add_reaction("✅")


@pr.command(name="iniciar")
async def init(ctx, *args):
    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    if lt:
        await ctx.message.add_reaction("❌")
        await ctx.channel.send("There is an active lightning talk!")
        return

    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    message = await channel.send(render(templates.NEW_LIGHTNING_TALK))
    await message.add_reaction("☝️")
    await db.create_lightning_talk(ctx.guild.id, message.id)
    await ctx.message.add_reaction("✅")
    logger.info(
        f"Lightning talk initialized. guild_id={ctx.guild.id!r}, message_id={message.id!r}"
    )


@pr.command(name="aviso")
async def anouncement(ctx, channel: discord.TextChannel, minutes: int, *args):
    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    if lt:
        await ctx.message.add_reaction("❌")
        await ctx.channel.send("There is an active lightning talk!")
        return

    hours = minutes // 60
    minutes = minutes % 60
    await channel.send(
        render(templates.ANNOUNCEMENT, waiting_time=f"{hours:02d} : {minutes:02d}")
    )
    await ctx.message.add_reaction("✅")


@pr.command(name="encerrar-inscrições")
async def close(ctx, *args):
    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    if not lt or not lt["open_registration"]:
        await ctx.message.add_reaction("❌")
        await ctx.channel.send(
            "There is no lightning talk in progress or open for registration!"
        )
        return

    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    message = await channel.fetch_message(lt["message_id"])
    await db.close_lightning_talk(lt["guild_id"], lt["message_id"])

    await message.edit(content=render(templates.NOT_ACTIVE_LIGHTNING_TALK))
    await message.clear_reactions()
    await ctx.message.add_reaction("✅")


@pr.command(name="chamada")
@fail_command_on(
    lt_not_in_progress,
    lt_speakers_defined,
)
async def define_speakers(ctx, *args):
    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    speakers_queue = lt["speakers_queue"]
    shuffle(speakers_queue)

    speakers = {}
    for speaker in speakers_queue:
        speakers[str(speaker)] = {
            "user_id": speaker,
            "confirmed": False,
            "invited": False,
        }

    await db.set_speakers_order(lt, speakers)
    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    message = await channel.fetch_message(lt["message_id"])
    await message.edit(
        content=render(templates.LIGHTNING_TALK_SPEAKERS_ORDER, speakers=lt["speakers"])
    )
    await ctx.message.add_reaction("✅")


@pr.command(name="convidar")
async def invite(ctx, user: discord.User, link: str, *args):
    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    prechecks = [
        not lt,
        lt.get("open_registration"),
        not lt.get("in_progress"),
        not lt.get("speakers"),
    ]
    if any(prechecks):
        await ctx.message.add_reaction("❌")
        await ctx.channel.send("Não foi possível convidar palestrante")
        return

    if user.id not in lt["speakers_queue"]:
        await ctx.message.add_reaction("❌")
        await ctx.channel.send("Palestrante não está na lista de usuários")
        return

    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)

    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    message = await channel.fetch_message(lt["message_id"])
    await message.edit(
        content=render(templates.LIGHTNING_TALK_SPEAKERS_ORDER, speakers=lt["speakers"])
    )


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    message = reaction.message
    guild_id = message.guild.id

    lt = await db.check_in_progress_lightning_talk(guild_id)
    checks = [
        not lt,
        lt.get("message_id") != message.id,
        not lt.get("in_progress"),
        not lt.get("open_registration"),
        user.bot,
    ]
    if any(checks):
        logger.debug(f"Ignoring reaction removed. reaction={reaction!r}, user={user!r}")
        return

    if reaction.emoji == JOIN_QUEUE_EMOJI:
        await db.add_speaker_to_queue(lt, user.id)
        logger.info(
            f"User added to speakers queue. guild_id={guild_id!r}, user={user!r}"
        )
        lt = await db.check_in_progress_lightning_talk(guild_id)
        await message.edit(
            content=render(
                templates.LIGHTNING_TALK_IN_PROGRESS, speakers=lt["speakers_queue"]
            )
        )


@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    message = reaction.message
    guild_id = message.guild.id

    lt = await db.check_in_progress_lightning_talk(guild_id)
    checks = [
        not lt,
        lt.get("message_id") != message.id,
        not lt.get("in_progress"),
        not lt.get("open_registration"),
        user.bot,
    ]
    if any(checks):
        logger.debug(f"Ignoring reaction added. reaction={reaction!r}, user={user!r}")
        return

    await db.add_speaker_to_queue(lt, user.id)
    await db.remove_speaker_from_queue(lt, user.id)
    logger.info(f"User added to speakers queue. guild_id={guild_id!r}, user={user!r}")
    lt = await db.check_in_progress_lightning_talk(guild_id)
    await message.edit(
        content=render(
            templates.LIGHTNING_TALK_IN_PROGRESS, speakers=lt["speakers_queue"]
        )
    )


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
