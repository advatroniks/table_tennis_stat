from aiogram.dispatcher.filters.state import State, StatesGroup



class MembersStates(StatesGroup):

    commit_game_to_database = State()