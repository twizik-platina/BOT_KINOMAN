from telebot import types


def get_screen_8_viewing_keyboard(
    viewing_id: int,
    page: int,
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            "Написать заметку",
            callback_data=f"note:{viewing_id}:{page}",
        ),
        types.InlineKeyboardButton(
            "Назад к истории",
            callback_data=f"history:{page}",
        ),
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data="menu",
        ),
    )

    return keyboard
