from telebot import types


def get_screen_2_main_menu_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            "Список премьер фильмов недели",
            callback_data="premieres",
        ),
        types.InlineKeyboardButton(
            "Кинотеатры и фильмы в прокате",
            callback_data="nearby",
        ),
        types.InlineKeyboardButton(
            "История просмотров",
            callback_data="history:0",
        ),
    )

    return keyboard
