import logging

from telebot.states.sync.context import StateContext

from api.movies_api import MoviesApiError
from bot_instance import bot
from services.kinoman_services import get_week_premieres
from ui.screen_3_premieres.keyboards import get_screen_3_premieres_keyboard
from ui.screen_3_premieres.texts import get_screen_3_premieres_text
from ui.states import KinomanStates


logger = logging.getLogger(__name__)


def show_screen_3_premieres(chat_id: int, state: StateContext) -> None:
    state.set(KinomanStates.screen_3_premieres)

    try:
        movies = get_week_premieres()
        text = get_screen_3_premieres_text(movies)
    except MoviesApiError as exc:
        logger.exception("Ошибка Kinopoisk.dev")
        text = "Сервис премьер временно недоступен."

    bot.send_message(
        chat_id,
        text,
        reply_markup=get_screen_3_premieres_keyboard(),
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "menu",
    state=KinomanStates.screen_3_premieres,
)
def callback_screen_3_menu_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
