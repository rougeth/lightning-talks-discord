from unittest import mock
import pytest

from lightning import bot


@pytest.mark.asyncio
@mock.patch("lightning.bot.get_or_create_lightning_talk_channel")
@mock.patch("lightning.bot.db", new_callable=mock.AsyncMock)
async def test_init(mocked_db, mocked_get_or_create_lightning_talk_channel):

    mocked_ctx = mock.AsyncMock()
    mocked_channel = mock.AsyncMock()
    mocked_message = mock.AsyncMock()

    mocked_db.check_active_lightning_talk.return_value = None
    mocked_get_or_create_lightning_talk_channel.return_value = mocked_channel
    mocked_channel.send.return_value = mocked_message

    await bot.init(mocked_ctx)

    mocked_db.check_active_lightning_talk.assert_awaited_once_with(mocked_ctx.guild.id)
    mocked_get_or_create_lightning_talk_channel.assert_awaited_once_with(
        mocked_ctx.guild
    )
    mocked_channel.send.assert_awaited_once()
    mocked_db.create_lightning_talk.assert_awaited_once_with(
        mocked_ctx.guild.id, mocked_message.id
    )
    mocked_ctx.message.add_reaction.assert_awaited_once()


@pytest.mark.asyncio
@mock.patch("bot.db.check_active_lightning_talk")
async def test_init_lt_active(mocked_check_active_lightning_talk):
    mocked_ctx = mock.AsyncMock()
    mocked_ctx.guild.id = 12345

    await bot.init(mocked_ctx)

    mocked_check_active_lightning_talk.assert_awaited_once_with(mocked_ctx.guild.id)
    mocked_ctx.channel.send.assert_awaited_once()


@pytest.mark.asyncio
@mock.patch("bot.db.close_lightning_talk")
@mock.patch(
    "bot.db.check_active_lightning_talk",
    return_value={"guild_id": "guild-id", "message_id": "message-id"},
)
async def test_close(
    mocked_check_active_lightning_talk, mocked_close_lightning_talk
):
    mocked_ctx = mock.AsyncMock()
    mocked_ctx.guild.id = "ctx-guild-id"

    await bot.close(mocked_ctx)

    mocked_ctx.channel.send.assert_not_awaited()
    mocked_check_active_lightning_talk.assert_awaited_once_with(mocked_ctx.guild.id)
    mocked_close_lightning_talk.assert_awaited_once_with("guild-id", "message-id")
    mocked_ctx.fetch_message.assert_awaited_once_with("message-id")
    mocked_ctx.fetch_message.return_value.edit.assert_awaited_once()
    mocked_ctx.message.add_reaction.assert_awaited_once()


@pytest.mark.asyncio
@mock.patch("bot.db.check_active_lightning_talk", return_value=None)
async def test_close_no_lt_active(mocked_check_active_lightning_talk):
    mocked_ctx = mock.AsyncMock()
    mocked_ctx.guild.id = 12345

    await bot.close(mocked_ctx)

    mocked_check_active_lightning_talk.assert_awaited_once_with(mocked_ctx.guild.id)
    mocked_ctx.channel.send.assert_awaited_once()
