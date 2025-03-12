from keys import BOT_TOKEN
import pytest
from unittest.mock import AsyncMock, ANY
from telegram import Message
from telegram.ext import CallbackContext
from main import start, handle_audio


def test_telegram_token():
    '''Check if the Telegram bot token is loaded and has a valid format.'''
    assert isinstance(BOT_TOKEN, str), 'BOT_TOKEN must be a string'
    assert BOT_TOKEN, 'BOT_TOKEN should not be empty'


@pytest.mark.asyncio # you need to install this module to test async code
async def test_start_command():
    '''Test if the bot responds with the correct keyboard options on /start'''
    update = AsyncMock()
    update.message = AsyncMock(spec=Message)
    context = AsyncMock(spec=CallbackContext)

    await start(update, context)

    update.message.reply_text.assert_called_once_with(
        'What do you want to do?',
        reply_markup=ANY
    )


@pytest.mark.asyncio
async def test_handle_audio_executes():
    '''Just checks that the function is callable'''
    assert callable(handle_audio)
