from telebot.states import State, StatesGroup


class KinomanStates(StatesGroup):
    screen_1_start = State()
    screen_2_main_menu = State()
    screen_3_premieres = State()
    screen_4_city_input = State()
    screen_5_cinema_date = State()
    screen_6_movies = State()
    screen_7_history = State()
    screen_8_viewing_info = State()
    screen_9_note_input = State()
