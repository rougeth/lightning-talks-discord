import asyncio
from unittest import mock

import discord
import pytest

from lightning.bot import (
    CATEGORY_NAME,
    CHANNEL_NAME,
    get_or_create_lightning_talk_channel,
)


@pytest.mark.asyncio
async def test_get_or_create_lightning_talk_channel_no_category():
    mocked_category = mock.AsyncMock()

    mocked_guild = mock.AsyncMock()
    mocked_guild.create_category.return_value = mocked_category

    await get_or_create_lightning_talk_channel(mocked_guild)

    mocked_guild.create_category.assert_awaited_once_with(CATEGORY_NAME)
    mocked_category.create_text_channel.assert_awaited_once_with(CHANNEL_NAME)


@pytest.mark.asyncio
async def test_get_or_create_lightning_talk_channel_no_channel():
    mocked_category = mock.AsyncMock(
        text_channels=[], type=discord.ChannelType.category
    )
    mocked_category.name = CATEGORY_NAME

    mocked_guild = mock.AsyncMock()
    mocked_guild.fetch_channels.return_value = [mocked_category]

    await get_or_create_lightning_talk_channel(mocked_guild)

    mocked_guild.create_category.assert_not_awaited()
    mocked_category.create_text_channel.assert_awaited_once_with(CHANNEL_NAME)


@pytest.mark.asyncio
async def test_get_or_create_lightning_talk_channel_with_category_and_channel():
    mocked_channel = mock.AsyncMock()
    mocked_channel.name = CHANNEL_NAME

    mocked_category = mock.AsyncMock(
        text_channels=[mocked_channel], type=discord.ChannelType.category
    )
    mocked_category.name = CATEGORY_NAME

    mocked_guild = mock.AsyncMock()
    mocked_guild.fetch_channels.return_value = [mocked_category]

    await get_or_create_lightning_talk_channel(mocked_guild)

    mocked_guild.create_category.assert_not_awaited()
    mocked_category.create_text_channel.assert_not_awaited()
