from telebot import types


def get_screen_3_premieres_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data="menu",
        )
    )
    return keyboard
