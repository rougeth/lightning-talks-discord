from functools import wraps
import inspect
from typing import Optional

from discord.ext import commands
from jinja2 import Template
from loguru import logger

import db


def render(template, **kwargs):
    t = Template(template)
    content = t.render(**kwargs)
    return "**[beta]**\n" + content


def speakers_defined(ctx: commands.Context):
    if not ctx.lt.get("speakers"):
        raise Exception("Lista de palestrantes ainda não foi definida")


def speakers_not_defined(ctx: commands.Context):
    if ctx.lt.get("speakers"):
        raise Exception("Lista de palestrantes já foi definida")


def is_open_for_registration(ctx: commands.Context):
    if not ctx.lt.get("open_registration"):
        raise Exception("Inscrições não estão abertas")


def is_registration_closed(ctx: commands.Context):
    if ctx.lt.get("open_registration"):
        raise Exception("Inscrições não estão abertas")


async def no_lt_in_progress(ctx: commands.Context):
    lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
    if lt:
        raise Exception("Já existe uma Palestra Relâmpago em andamento")


def check_all(*functions):
    def decorator(f):
        @wraps(f)
        async def wrapper(ctx, *args, **kwargs):
            for check in functions:
                try:
                    if inspect.iscoroutinefunction(check):
                        await check(ctx)
                    else:
                        check(ctx)
                except Exception as e:
                    await ctx.message.add_reaction("❌")
                    await ctx.channel.send(str(e))
                    return
            return await f(ctx, *args, **kwargs)

        return wrapper

    return decorator


def ctx_with_lt(function):
    @wraps(function)
    async def wrapper(ctx: commands.Context, *args, **kwargs):
        lt = await db.check_in_progress_lightning_talk(ctx.guild.id)
        if not lt:
            logger.info(f"Lightning Talk not found for guild. guild_id={ctx.guild.id}")
            await ctx.message.add_reaction("❌")
            await ctx.send(
                content="Você precisa iniciar uma palestra relâmpago primeiro. Para ajuda, use o comando: lt!ajuda"
            )
            return

        ctx.lt = lt
        return await function(ctx, *args, **kwargs)

    return wrapper
