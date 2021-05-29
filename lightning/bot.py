import re
import typing
from collections import defaultdict
from dataclasses import dataclass, field

import discord
from discord.ext import commands
from discord.ext.tasks import loop

from decouple import config


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.group(invoke_without_command=True)
async def pr(ctx, *args):
    await ctx.channel.send("TODO: help")


if __name__ == "__main__":
    DISCORD_TOKEN = config("DISCORD_TOKEN")
    bot.run(DISCORD_TOKEN)
