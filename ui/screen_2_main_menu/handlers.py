from telebot.states.sync.context import StateContext

from bot_instance import bot
from ui.screen_2_main_menu.keyboards import get_screen_2_main_menu_keyboard
from ui.screen_2_main_menu.texts import MAIN_MENU_TEXT
from ui.states import KinomanStates


def show_screen_2_main_menu(chat_id: int, state: StateContext) -> None:
    # При возврате в меню очищаем временные данные предыдущего сценария.
    state.delete()
    state.set(KinomanStates.screen_2_main_menu)

    bot.send_message(
        chat_id,
        MAIN_MENU_TEXT,
        reply_markup=get_screen_2_main_menu_keyboard(),
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "premieres",
    state=KinomanStates.screen_2_main_menu,
)
def callback_premieres_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_3_premieres.handlers import show_screen_3_premieres

    show_screen_3_premieres(call.message.chat.id, state)


@bot.callback_query_handler(
    func=lambda call: call.data == "nearby",
    state=KinomanStates.screen_2_main_menu,
)
def callback_nearby_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_4_city_input.handlers import show_screen_4_city_input

    show_screen_4_city_input(call.message.chat.id, state)


@bot.callback_query_handler(
    func=lambda call: call.data == "history:0",
    state=KinomanStates.screen_2_main_menu,
)
def callback_history_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_7_history.handlers import show_screen_7_history

    show_screen_7_history(
        call.message.chat.id,
        call.from_user.id,
        state,
        page=0,
    )
