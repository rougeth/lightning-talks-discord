from unittest import mock
import pytest

from lightning.bot import iniciar


@pytest.mark.asyncio
@mock.patch("lightning.bot.get_or_create_lightning_talk_channel")
@mock.patch("lightning.bot.db", new_callable=mock.AsyncMock)
async def test_iniciar(mocked_db, mocked_get_or_create_lightning_talk_channel):

    mocked_ctx = mock.AsyncMock()
    mocked_channel = mock.AsyncMock()
    mocked_message = mock.AsyncMock()

    mocked_db.check_active_lightning_talk.return_value = None
    mocked_get_or_create_lightning_talk_channel.return_value = mocked_channel
    mocked_channel.send.return_value = mocked_message

    await iniciar(mocked_ctx)

    mocked_db.check_active_lightning_talk.assert_awaited_once_with(mocked_ctx.guild.id)
    mocked_get_or_create_lightning_talk_channel.assert_awaited_once_with(mocked_ctx.guild)
    mocked_channel.send.assert_awaited_once()
    mocked_db.create_lightning_talk.assert_awaited_once_with(mocked_ctx.guild.id, mocked_message.id)
    mocked_ctx.message.add_reaction.assert_awaited_once()


@pytest.mark.asyncio
@mock.patch("bot.db.check_active_lightning_talk")
async def test_iniciar_lt_active(mocked_check_active_lightning_talk):
    mocked_ctx = mock.AsyncMock()
    mocked_ctx.guild.id = 12345

    await iniciar(mocked_ctx)

    mocked_check_active_lightning_talk.assert_awaited_once_with(mocked_ctx.guild.id)
    mocked_ctx.channel.send.assert_awaited_once()


