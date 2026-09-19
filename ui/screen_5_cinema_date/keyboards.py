from telebot import types

from models.cinema import Cinema


def get_screen_5_cinemas_keyboard(
    cinemas: list[Cinema],
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for index, _cinema in enumerate(cinemas):
        keyboard.add(
            types.InlineKeyboardButton(
                f"Выбрать кинотеатр {index + 1}",
                callback_data=f"cinema:{index}",
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "Назад",
            callback_data="back_city",
        ),
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data="menu",
        ),
    )

    return keyboard


def get_screen_5_date_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(
            "Назад к кинотеатрам",
            callback_data="back_cinemas",
        ),
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data="menu",
        ),
    )
    return keyboard
