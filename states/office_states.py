from aiogram.dispatcher.filters.state import State, StatesGroup


class OfficeStates(StatesGroup):

    get_player_for_rate = State()