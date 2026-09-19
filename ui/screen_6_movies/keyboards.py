from telebot import types

from models.movie import Movie


def get_screen_6_movies_keyboard(
    movies: list[Movie],
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for index, _movie in enumerate(movies):
        keyboard.add(
            types.InlineKeyboardButton(
                f"Сохранить посещение для фильма №{index + 1}",
                callback_data=f"movie:{index}",
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "Назад",
            callback_data="back_cinemas",
        ),
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data="menu",
        ),
    )

    return keyboard
