from telebot import types


def get_screen_9_note_keyboard(
    viewing_id: int,
    page: int,
) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            "Отмена",
            callback_data=f"cancel_note:{viewing_id}:{page}",
        ),
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data="menu",
        ),
    )

    return keyboard
