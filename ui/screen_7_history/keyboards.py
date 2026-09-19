from telebot import types

from models.viewing import Viewing


def get_screen_7_history_keyboard(
    items: list[Viewing],
    page: int,
    total_pages: int,
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for index, viewing in enumerate(items):
        keyboard.add(
            types.InlineKeyboardButton(
                f"Выбрать посещение {index + 1}",
                callback_data=f"viewing:{viewing.id}:{page}",
            )
        )

    navigation = []

    if page > 0:
        navigation.append(
            types.InlineKeyboardButton(
                "Назад",
                callback_data=f"history:{page - 1}",
            )
        )

    if page < total_pages - 1:
        navigation.append(
            types.InlineKeyboardButton(
                "Вперёд",
                callback_data=f"history:{page + 1}",
            )
        )

    if navigation:
        keyboard.row(*navigation)

    keyboard.add(
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data="menu",
        )
    )

    return keyboard
