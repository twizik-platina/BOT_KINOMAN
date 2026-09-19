from telebot.states.sync.context import StateContext

from bot_instance import bot
from ui.screen_1_start.keyboards import get_screen_1_start_keyboard
from ui.screen_1_start.texts import START_TEXT
from ui.states import KinomanStates


@bot.message_handler(commands=["start"])
def command_screen_1_start_handler(message, state: StateContext):
    # /start работает из любого экрана и полностью сбрасывает старый сценарий.
    state.delete()
    state.set(KinomanStates.screen_1_start)

    bot.send_message(
        message.chat.id,
        START_TEXT,
        reply_markup=get_screen_1_start_keyboard(),
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "start",
    state=KinomanStates.screen_1_start,
)
def callback_screen_1_start_handler(call, state: StateContext):
    bot.answer_callback_query(call.id)

    from ui.screen_2_main_menu.handlers import show_screen_2_main_menu

    show_screen_2_main_menu(call.message.chat.id, state)
