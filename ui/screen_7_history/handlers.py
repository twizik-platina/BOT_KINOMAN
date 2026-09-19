import logging

from telebot.states.sync.context import StateContext

from bot_instance import bot
from repositories.viewings_repository import RepositoryError
from services.kinoman_services import get_history
from ui.screen_7_history.keyboards import get_screen_7_history_keyboard
from ui.screen_7_history.texts import get_screen_7_history_text
from ui.states import KinomanStates


logger = logging.getLogger(__name__)


def show_screen_7_history(
    chat_id: int,
    user_id: int,
    state: StateContext,
    page: int = 0,
) -> None:
    state.set(KinomanStates.screen_7_history)

    try:
        history = get_history(user_id, page)
    except RepositoryError:
        logger.exception("Ошибка загрузки истории")
        bot.send_message(chat_id, "Не удалось загрузить историю.")
        return

    state.add_data(history_page=history.page)

    bot.send_message(
        chat_id,
        get_screen_7_history_text(
            history.items,
            history.page,
            history.total_pages,
        ),
        reply_markup=get_screen_7_history_keyboard(
            history.items,
            history.page,
            history.total_pages,
        ),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("history:"),
    state=KinomanStates.screen_7_history,
)
def callback_history_page_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    try:
        page = int(call.data.split(":", 1)[1])
    except ValueError:
        page = 0

    show_screen_7_history(
        call.message.chat.id,
        call.from_user.id,
        state,
        page,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("viewing:"),
    state=KinomanStates.screen_7_history,
)
def callback_history_viewing_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    try:
        _, viewing_id, page = call.data.split(":")
    except ValueError:
        return

    from ui.screen_8_viewing_info.handlers import show_screen_8_viewing_info

    show_screen_8_viewing_info(
        call.message.chat.id,
        call.from_user.id,
        state,
        int(viewing_id),
        int(page),
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "menu",
    state=KinomanStates.screen_7_history,
)
def callback_screen_7_menu_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
