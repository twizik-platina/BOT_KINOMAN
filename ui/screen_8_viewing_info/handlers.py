import logging

from telebot.states.sync.context import StateContext

from bot_instance import bot
from repositories.viewings_repository import RepositoryError
from services.kinoman_services import get_viewing
from ui.screen_8_viewing_info.keyboards import get_screen_8_viewing_keyboard
from ui.screen_8_viewing_info.texts import get_screen_8_viewing_text
from ui.states import KinomanStates


logger = logging.getLogger(__name__)


def show_screen_8_viewing_info(
    chat_id: int,
    user_id: int,
    state: StateContext,
    viewing_id: int,
    history_page: int = 0,
) -> None:
    state.set(KinomanStates.screen_8_viewing_info)

    try:
        viewing = get_viewing(viewing_id, user_id)
    except RepositoryError:
        logger.exception("Ошибка загрузки посещения")
        bot.send_message(chat_id, "Не удалось загрузить посещение.")
        return

    if viewing is None:
        bot.send_message(chat_id, "Посещение не найдено.")
        return

    state.add_data(
        selected_viewing_id=viewing_id,
        history_page=history_page,
    )

    bot.send_message(
        chat_id,
        get_screen_8_viewing_text(viewing),
        reply_markup=get_screen_8_viewing_keyboard(
            viewing_id,
            history_page,
        ),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("note:"),
    state=KinomanStates.screen_8_viewing_info,
)
def callback_note_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    try:
        _, viewing_id, page = call.data.split(":")
    except ValueError:
        return

    from ui.screen_9_note_input.handlers import show_screen_9_note_input

    show_screen_9_note_input(
        call.message.chat.id,
        state,
        int(viewing_id),
        int(page),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("history:"),
    state=KinomanStates.screen_8_viewing_info,
)
def callback_screen_8_history_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    try:
        page = int(call.data.split(":", 1)[1])
    except ValueError:
        page = 0

    from ui.screen_7_history.handlers import show_screen_7_history

    show_screen_7_history(
        call.message.chat.id,
        call.from_user.id,
        state,
        page,
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "menu",
    state=KinomanStates.screen_8_viewing_info,
)
def callback_screen_8_menu_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
