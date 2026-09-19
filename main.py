"""Точка входа в приложение Бот-Киноман."""



import logging

from telebot import custom_filters
from telebot.states.sync.middleware import StateMiddleware

from bot_instance import bot
from services.kinoman_services import prepare_database

# Импорт модулей регистрирует декораторы-обработчики экранов.
import ui.screen_1_start.handlers  # noqa: F401
import ui.screen_2_main_menu.handlers  # noqa: F401
import ui.screen_3_premieres.handlers  # noqa: F401
import ui.screen_4_city_input.handlers  # noqa: F401
import ui.screen_5_cinema_date.handlers  # noqa: F401
import ui.screen_6_movies.handlers  # noqa: F401
import ui.screen_7_history.handlers  # noqa: F401
import ui.screen_8_viewing_info.handlers  # noqa: F401
import ui.screen_9_note_input.handlers  # noqa: F401


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

prepare_database()

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.setup_middleware(StateMiddleware(bot))

print("Бот-Киноман запущен")

bot.infinity_polling(
    skip_pending=True,
    timeout=30,
    long_polling_timeout=30,
)
