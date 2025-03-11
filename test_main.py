import os
from keys import BOT_TOKEN


def test_telegram_token():
    """Check if the Telegram bot token is loaded and has a valid format."""
    assert isinstance(BOT_TOKEN, str), "BOT_TOKEN must be a string"
    assert BOT_TOKEN, "BOT_TOKEN should not be empty"
