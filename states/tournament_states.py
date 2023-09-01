from aiogram.dispatcher.filters.state import StatesGroup, State


class TournamentStaes(StatesGroup):

    insert_members_count_state = State()
    insert_members_name_surname = State()
    insert_list_members_name_surname = State()
    absolute_insert = State()
    absolute_insert_1 = State()
    users_tournament_menu = State()
    confirm_member_state = State()
    tournament_begin_state = State()
