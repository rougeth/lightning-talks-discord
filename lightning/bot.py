import re
import typing
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import shuffle

import discord
from discord.ext import commands
from discord.ext.tasks import loop
from decouple import config
from loguru import logger

import templates
import db
import helpers


DISCORD_TOKEN = config("DISCORD_TOKEN")
CATEGORY_NAME = "Palestras Relâmpago"
CHANNEL_NAME = "quero-participar"
ORG_CHANNEL_NAME = "org-only"

JOIN_QUEUE_EMOJI = "☝️"
CONFIRMATION_EMOJI = "✅"
DECLINE_INVITATION_EMOJI = "❌"


bot = commands.Bot(command_prefix="pr!", intents=discord.Intents.all())


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


@bot.command()
@commands.guild_only()
async def build(ctx, org_role: discord.Role, *args):
    await get_or_create_lightning_talk_channel(ctx.guild, org_role)
    await ctx.message.add_reaction(CONFIRMATION_EMOJI)


@bot.command(name="iniciar")
@helpers.check_all(helpers.no_lt_in_progress)
@commands.guild_only()
async def init(ctx, *args):
    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    await channel.purge()
    
    message = await channel.send(helpers.render(templates.NEW_LIGHTNING_TALK))
    await message.add_reaction("☝️")
    await db.create_lightning_talk(ctx.guild.id, message.id)
    await ctx.message.add_reaction(CONFIRMATION_EMOJI)
    logger.info(
        f"Lightning talk initialized. guild_id={ctx.guild.id!r}, message_id={message.id!r}"
    )


@bot.command(name="encerrar-inscrições")
@helpers.ctx_with_lt
@helpers.check_all(helpers.is_open_for_registration)
@commands.guild_only()
async def close(ctx, *args):
    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    message = await channel.fetch_message(ctx.lt["message_id"])
    await db.close_lightning_talk(ctx.lt["guild_id"], ctx.lt["message_id"])

    await message.edit(content=helpers.render(templates.NOT_ACTIVE_LIGHTNING_TALK))
    await message.clear_reactions()
    await ctx.message.add_reaction(CONFIRMATION_EMOJI)


@bot.command(name="chamada")
@helpers.ctx_with_lt
@helpers.check_all(
    helpers.is_registration_closed,
    helpers.speakers_not_defined,
)
@commands.guild_only()
async def define_speakers(ctx, *args):
    speakers_queue = ctx.lt["speakers_queue"]
    shuffle(speakers_queue)

    speakers = {}
    for speaker in speakers_queue:
        speakers[str(speaker)] = {
            "user_id": speaker,
            "confirmed": False,
            "invited": False,
        }

    await db.set_speakers_order(ctx.lt, speakers)
    ctx.lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    message = await channel.fetch_message(ctx.lt["message_id"])
    await message.edit(
        content=helpers.render(
            templates.LIGHTNING_TALK_SPEAKERS_ORDER, speakers=ctx.lt["speakers"]
        )
    )
    await ctx.message.add_reaction(CONFIRMATION_EMOJI)


@bot.command(name="convidar")
@helpers.ctx_with_lt
@helpers.check_all(
    helpers.is_registration_closed,
    helpers.speakers_defined,
)
@commands.guild_only()
async def invite(ctx, user: discord.User, link: str, *args):
    if user.id not in ctx.lt["speakers_queue"]:
        await ctx.message.add_reaction(DECLINE_INVITATION_EMOJI)
        await ctx.channel.send("Palestrante não está na lista de usuários")
        return

    message = await user.send(
        helpers.render(templates.INVITE, speaker=user.mention, link=link)
    )
    await db.invite_speaker(ctx.lt, user.id, message.id)
    await ctx.message.add_reaction(CONFIRMATION_EMOJI)


@bot.command(name="encerrar")
@helpers.ctx_with_lt
@helpers.check_all(
    helpers.is_registration_closed,
    helpers.speakers_defined,
)
@commands.guild_only()
async def finish(ctx, *_):
    await db.finish_lightning_talk(ctx.lt)
    channel = await get_or_create_lightning_talk_channel(ctx.guild, None)
    message = await channel.fetch_message(ctx.lt["message_id"])
    await message.edit(content=helpers.render(templates.FINISH_LIGHTNING_TALK))
    await ctx.message.add_reaction(CONFIRMATION_EMOJI)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if not reaction.message.guild:
        logger.debug("Reaction not in a channel")
        return

    message = reaction.message
    lt = await db.check_in_progress_lightning_talk(message.guild.id)
    checks = [
        not lt,
        lt.get("message_id") != message.id,
        not lt.get("open_registration"),
        user.bot,
    ]
    if any(checks):
        logger.debug(f"Ignoring reaction removed. reaction={reaction!r}, user={user!r}")
        return

    if reaction.emoji == JOIN_QUEUE_EMOJI:
        await db.add_speaker_to_queue(lt, user.id)
        logger.info(
            f"User added to speakers queue. guild_id={message.guild.id!r}, user={user!r}"
        )
        lt = await db.check_in_progress_lightning_talk(message.guild.id)
        await message.edit(
            content=helpers.render(
                templates.LIGHTNING_TALK_IN_PROGRESS, speakers=lt["speakers_queue"]
            )
        )


@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    if not reaction.message.guild:
        logger.debug("Reaction not in a channel")
        return

    message = reaction.message

    lt = await db.check_in_progress_lightning_talk(message.guild.id)
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
    logger.info(
        f"User added to speakers queue. guild_id={message.guild.id!r}, user={user!r}"
    )
    lt = await db.check_in_progress_lightning_talk(message.guild.id)
    await message.edit(
        content=helpers.render(
            templates.LIGHTNING_TALK_IN_PROGRESS, speakers=lt["speakers_queue"]
        )
    )


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
