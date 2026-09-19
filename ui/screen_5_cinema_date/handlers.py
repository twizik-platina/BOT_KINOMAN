import logging
from datetime import date, datetime

from telebot.states.sync.context import StateContext

from api.cinemas_api import CinemasApiError
from bot_instance import bot
from models.cinema import Cinema
from services.kinoman_services import get_cinemas, get_movies
from ui.screen_5_cinema_date.keyboards import (
    get_screen_5_cinemas_keyboard,
    get_screen_5_date_keyboard,
)
from ui.screen_5_cinema_date.texts import (
    DATE_PROMPT,
    get_screen_5_cinemas_text,
)
from ui.states import KinomanStates


logger = logging.getLogger(__name__)


def show_screen_5_cinema_date(
    chat_id: int,
    state: StateContext,
) -> None:
    with state.data() as data:
        location_slug = data.get("location_slug")

    if not location_slug:
        from ui.screen_4_city_input.handlers import show_screen_4_city_input
        show_screen_4_city_input(chat_id, state)
        return

    state.set(KinomanStates.screen_5_cinema_date)

    try:
        cinemas = get_cinemas(location_slug)
    except CinemasApiError as exc:
        logger.exception("Ошибка KudaGo при загрузке кинотеатров")
        bot.send_message(chat_id, str(exc))
        return

    state.add_data(
        cinemas=[
            {
                "id": cinema.id,
                "title": cinema.title,
                "address": cinema.address,
            }
            for cinema in cinemas
        ],
        selected_cinema=None,
        selected_date=None,
        movies=[],
    )

    bot.send_message(
        chat_id,
        get_screen_5_cinemas_text(cinemas),
        reply_markup=get_screen_5_cinemas_keyboard(cinemas),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cinema:"),
    state=KinomanStates.screen_5_cinema_date,
)
def callback_select_cinema_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    try:
        index = int(call.data.split(":", 1)[1])

        with state.data() as data:
            cinemas = data.get("cinemas", [])

        cinema = cinemas[index]
        state.add_data(selected_cinema=cinema)

        bot.send_message(
            call.message.chat.id,
            f"Выбран кинотеатр: {cinema['title']}\n\n{DATE_PROMPT}",
            reply_markup=get_screen_5_date_keyboard(),
        )

    except (ValueError, IndexError, KeyError):
        bot.send_message(
            call.message.chat.id,
            "Не удалось выбрать кинотеатр. Попробуйте ещё раз.",
        )


@bot.message_handler(
    state=KinomanStates.screen_5_cinema_date,
    content_types=["text"],
)
def message_screen_5_date_handler(message, state: StateContext):
    with state.data() as data:
        selected_cinema = data.get("selected_cinema")
        location_slug = data.get("location_slug")

    if not selected_cinema:
        bot.send_message(
            message.chat.id,
            "Сначала выберите кинотеатр кнопкой.",
        )
        return

    try:
        selected_date = datetime.strptime(
            message.text.strip(),
            "%d.%m.%Y",
        ).date()
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неверная дата. Используйте формат ДД.ММ.ГГГГ.",
        )
        return

    if selected_date < date.today():
        bot.send_message(
            message.chat.id,
            "Нельзя выбрать прошедшую дату.",
        )
        return

    try:
        movies = get_movies(
            location_slug,
            int(selected_cinema["id"]),
            selected_date,
        )
    except CinemasApiError as exc:
        logger.exception("Ошибка KudaGo при загрузке афиши")
        bot.send_message(
            message.chat.id,
            str(exc),
            reply_markup=get_screen_5_date_keyboard(),
        )
        return

    state.add_data(
        selected_date=selected_date.isoformat(),
        movies=[
            {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "poster_url": movie.poster_url,
            }
            for movie in movies
        ],
    )

    from ui.screen_6_movies.handlers import show_screen_6_movies

    show_screen_6_movies(message.chat.id, state)


@bot.callback_query_handler(
    func=lambda call: call.data == "back_city",
    state=KinomanStates.screen_5_cinema_date,
)
def callback_back_city_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_4_city_input.handlers import show_screen_4_city_input

    show_screen_4_city_input(call.message.chat.id, state)


@bot.callback_query_handler(
    func=lambda call: call.data == "back_cinemas",
    state=KinomanStates.screen_5_cinema_date,
)
def callback_back_cinemas_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)
    show_screen_5_cinema_date(call.message.chat.id, state)


@bot.callback_query_handler(
    func=lambda call: call.data == "menu",
    state=KinomanStates.screen_5_cinema_date,
)
def callback_screen_5_menu_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
