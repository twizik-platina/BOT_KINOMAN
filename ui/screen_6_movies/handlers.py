import logging
from datetime import date

from telebot.states.sync.context import StateContext

from bot_instance import bot
from models.cinema import Cinema
from models.city import City
from models.movie import Movie
from repositories.viewings_repository import RepositoryError
from services.kinoman_services import save_viewing
from ui.screen_6_movies.keyboards import get_screen_6_movies_keyboard
from ui.screen_6_movies.texts import get_screen_6_movies_text
from ui.states import KinomanStates


logger = logging.getLogger(__name__)


def _load_movies_from_state(state: StateContext) -> tuple[str, str, list[Movie]]:
    with state.data() as data:
        cinema_data = data.get("selected_cinema") or {}
        date_iso = data.get("selected_date")
        movies_data = data.get("movies", [])

    movies = [
        Movie(
            id=int(item["id"]),
            title=item["title"],
            description=item.get("description") or "",
            poster_url=item.get("poster_url"),
        )
        for item in movies_data
    ]

    date_text = ""

    if date_iso:
        date_text = date.fromisoformat(date_iso).strftime("%d.%m.%Y")

    return cinema_data.get("title", "Кинотеатр"), date_text, movies


def show_screen_6_movies(
    chat_id: int,
    state: StateContext,
) -> None:
    state.set(KinomanStates.screen_6_movies)

    cinema_name, date_text, movies = _load_movies_from_state(state)

    bot.send_message(
        chat_id,
        get_screen_6_movies_text(
            cinema_name,
            date_text,
            movies,
        ),
        reply_markup=get_screen_6_movies_keyboard(movies),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("movie:"),
    state=KinomanStates.screen_6_movies,
)
def callback_save_movie_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    try:
        index = int(call.data.split(":", 1)[1])

        with state.data() as data:
            city_data = data["city"]
            cinema_data = data["selected_cinema"]
            selected_date = date.fromisoformat(data["selected_date"])
            movie_data = data["movies"][index]

        city = City(
            name=city_data["name"],
            lat=float(city_data["lat"]),
            lng=float(city_data["lng"]),
        )
        cinema = Cinema(
            id=int(cinema_data["id"]),
            title=cinema_data["title"],
            address=cinema_data["address"],
        )
        movie = Movie(
            id=int(movie_data["id"]),
            title=movie_data["title"],
            description=movie_data.get("description") or "",
            poster_url=movie_data.get("poster_url"),
        )

        viewing = save_viewing(
            tg_user_id=call.from_user.id,
            city=city,
            cinema=cinema,
            selected_date=selected_date,
            movie=movie,
        )

        from ui.screen_8_viewing_info.handlers import show_screen_8_viewing_info

        show_screen_8_viewing_info(
            call.message.chat.id,
            call.from_user.id,
            state,
            viewing.id,
            history_page=0,
        )

    except (ValueError, IndexError, KeyError, RepositoryError):
        logger.exception("Не удалось сохранить посещение")
        bot.send_message(
            call.message.chat.id,
            "Не удалось сохранить посещение. Попробуйте ещё раз.",
        )


@bot.callback_query_handler(
    func=lambda call: call.data == "back_cinemas",
    state=KinomanStates.screen_6_movies,
)
def callback_screen_6_back_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_5_cinema_date.handlers import show_screen_5_cinema_date

    show_screen_5_cinema_date(call.message.chat.id, state)


@bot.callback_query_handler(
    func=lambda call: call.data == "menu",
    state=KinomanStates.screen_6_movies,
)
def callback_screen_6_menu_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
