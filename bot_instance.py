"""Общий экземпляр Telegram-бота.

Сделано так же, как в эталонном TravelHunter:
один объект bot создаётся в отдельном файле и импортируется экранами.
"""

import telebot
from telebot.storage import StateMemoryStorage

from config import Config


config = Config.from_file()
state_storage = StateMemoryStorage()

bot = telebot.TeleBot(
    config.bot_token,
    state_storage=state_storage,
    use_class_middlewares=True,
)
