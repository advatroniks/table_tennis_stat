from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class PlayerRegistrationState(StatesGroup):
    reg_name = State()
    reg_surname = State()
    reg_age = State()
    reg_city = State()
    reg_game_style = State()
