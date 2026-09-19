import logging

from telebot.states.sync.context import StateContext

from api.cinemas_api import UnsupportedCityError
from api.cities_api import CityApiError
from bot_instance import bot
from services.kinoman_services import find_city
from ui.screen_4_city_input.keyboards import get_screen_4_city_input_keyboard
from ui.screen_4_city_input.texts import CITY_NOT_FOUND, CITY_PROMPT
from ui.states import KinomanStates


logger = logging.getLogger(__name__)


def show_screen_4_city_input(chat_id: int, state: StateContext) -> None:
    state.delete()
    state.set(KinomanStates.screen_4_city_input)

    bot.send_message(
        chat_id,
        CITY_PROMPT,
        reply_markup=get_screen_4_city_input_keyboard(),
    )


@bot.message_handler(
    state=KinomanStates.screen_4_city_input,
    content_types=["text"],
)
def message_screen_4_city_input_handler(message, state: StateContext):
    try:
        city, location_slug = find_city(message.text)

        if city is None or location_slug is None:
            bot.send_message(message.chat.id, CITY_NOT_FOUND)
            return

        state.add_data(
            city={
                "name": city.name,
                "lat": city.lat,
                "lng": city.lng,
            },
            location_slug=location_slug,
        )

        from ui.screen_5_cinema_date.handlers import show_screen_5_cinema_date

        show_screen_5_cinema_date(message.chat.id, state)

    except UnsupportedCityError as exc:
        bot.send_message(
            message.chat.id,
            str(exc),
            reply_markup=get_screen_4_city_input_keyboard(),
        )

    except CityApiError as exc:
        logger.exception("Ошибка GeoNames")
        bot.send_message(
            message.chat.id,
            str(exc),
            reply_markup=get_screen_4_city_input_keyboard(),
        )


@bot.callback_query_handler(
    func=lambda call: call.data == "menu",
    state=KinomanStates.screen_4_city_input,
)
def callback_screen_4_menu_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
