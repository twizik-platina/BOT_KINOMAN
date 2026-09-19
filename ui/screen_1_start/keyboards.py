from telebot import types


def get_screen_1_start_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "Старт",
            callback_data="start",
        )
    )
    return keyboard
