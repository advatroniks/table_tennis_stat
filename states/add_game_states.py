from aiogram.dispatcher.filters.state import StatesGroup, State

class AddGameStates(StatesGroup):

    select_type_game = State()
    select_rival = State()
    add_funn_game_score = State()
    add_game_score = State()
    add_sets_score = State()
    select_input_game_type = State()


class AddScoreSetsStates(StatesGroup):

    set_1 = State()
    set_2 = State()
    set_3 = State()
    set_4 = State()
    set_5 = State()
    set_6 = State()
    set_7 = State()