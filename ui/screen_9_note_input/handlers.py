import logging

from telebot.states.sync.context import StateContext

from bot_instance import bot
from repositories.viewings_repository import RepositoryError
from services.kinoman_services import save_note
from ui.screen_9_note_input.keyboards import get_screen_9_note_keyboard
from ui.screen_9_note_input.texts import NOTE_PROMPT
from ui.states import KinomanStates


logger = logging.getLogger(__name__)


def show_screen_9_note_input(
    chat_id: int,
    state: StateContext,
    viewing_id: int,
    history_page: int,
) -> None:
    state.set(KinomanStates.screen_9_note_input)
    state.add_data(
        selected_viewing_id=viewing_id,
        history_page=history_page,
    )

    bot.send_message(
        chat_id,
        NOTE_PROMPT,
        reply_markup=get_screen_9_note_keyboard(
            viewing_id,
            history_page,
        ),
    )


@bot.message_handler(
    state=KinomanStates.screen_9_note_input,
    content_types=["text"],
)
def message_screen_9_note_handler(message, state: StateContext):
    with state.data() as data:
        viewing_id = data.get("selected_viewing_id")
        page = int(data.get("history_page", 0))

    if viewing_id is None:
        bot.send_message(
            message.chat.id,
            "Не удалось определить посещение.",
        )
        return

    try:
        viewing = save_note(
            int(viewing_id),
            message.from_user.id,
            message.text,
        )

        if viewing is None:
            bot.send_message(message.chat.id, "Посещение не найдено.")
            return

    except ValueError as exc:
        bot.send_message(message.chat.id, str(exc))
        return

    except RepositoryError:
        logger.exception("Ошибка сохранения заметки")
        bot.send_message(
            message.chat.id,
            "Не удалось сохранить заметку.",
        )
        return

    from ui.screen_8_viewing_info.handlers import show_screen_8_viewing_info

    show_screen_8_viewing_info(
        message.chat.id,
        message.from_user.id,
        state,
        int(viewing_id),
        page,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cancel_note:"),
    state=KinomanStates.screen_9_note_input,
)
def callback_cancel_note_handler(call, state: StateContext):
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
    state=KinomanStates.screen_9_note_input,
)
def callback_screen_9_menu_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
