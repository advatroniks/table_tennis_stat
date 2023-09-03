from aiogram import Dispatcher
from states.member_tournament_states import *
from keyboards.tournaments_keyboards import *
from keyboards.members_tournament_keyboard import *
from handlers.tournaments_handlers import get_rival_and_table_number
from handlers.tournaments_handlers import check_player_is_in_tournament
from aiogram.dispatcher import FSMContext
from database.tournaments_db import *
from database.members_tournament_dp import *
from buffer import buffer
from bot_instance import bot

"""
Программа которая отвечает за взаимодействие с участником турнира.
"""


# Функция получает телеграм айди, на выходе дает ключ турнира, где на данный момент участник играет.
def get_tournament_key_for_members(telegram_id: str) -> str:
    for i in buffer:
        if i.find(str(telegram_id)) != -1:
            return i
        else:
            print('bad news')


# получить список всех участников турнира.
async def get_all_members_in_tournament(callback: types.CallbackQuery) -> None:
    tournament_key = get_tournament_key_for_members(callback.from_user.id)
    print('hello world')
    await callback.message.edit_text(text=buffer[tournament_key]['name_surname_members'],
                                     reply_markup=get_back_button())


async def button_back_to_tournament_menu(callback: types.CallbackQuery) -> None:
    telegram_id = str(callback.from_user.id)
    await check_player_is_in_tournament(telegram_id=telegram_id)


async def add_game_in_tournament(callback: types.CallbackQuery, state: FSMContext) -> None:
    await bot.edit_message_text(text='Укажите счет матча:',
                                message_id=callback.message.message_id,
                                reply_markup=add_game_keyboard(),
                                chat_id=callback.from_user.id)
    await MembersStates.commit_game_to_database.set()


async def commit_game_to_database(callback: types.CallbackQuery, state: FSMContext) -> None:
    print("start working functions commit_game_to_database...")
    first_player = callback.from_user.id
    second_player_table_set = await get_rival_and_table_number(telegram_id=str(first_player))
    second_player, table_number = second_player_table_set
    score = callback.data

    players_set = (first_player, second_player)

    tournament_key = get_tournament_key_for_members(telegram_id=first_player)
    tournament_id = buffer[tournament_key]["tournament_id"]

    await add_game_to_database(first_player=first_player,
                               second_player=second_player,
                               score=score,
                               tournament_id=tournament_id
                               )
    buffer[tournament_key]['game_counter'] -= 1

    for player in players_set:
        await bot.edit_message_text(text='Ожидайте вашего соперника.',
                                    chat_id=player,
                                    message_id=await get_message_id_in_active_tournament(telegram_id=player),
                                    reply_markup=get_tournament_menu_keyboard()
                                    )

    table_numer_digit = 2 * table_number - 1
    buffer[tournament_key]['table_conditions'][table_numer_digit] = 0
    buffer[tournament_key]['table_conditions'][table_numer_digit - 1] = 0

    print(buffer[tournament_key])
    await state.finish()


async def get_online_scoreboard(callback: types.CallbackQuery) -> None:
    tournament_key = get_tournament_key_for_members(telegram_id=callback.from_user.id)
    message_id = await get_message_id_in_active_tournament(telegram_id=callback.from_user.id)

    table_conditions = buffer[tournament_key]["table_conditions"]

    result = ''

    print(table_conditions)

    table_counter = 1
    players_counter = 0
    null_counter = 0

    for i in table_conditions:
        if i == 0 and null_counter == 0:
            result += f'{table_counter} - й Стол: Свободен'
            null_counter += 1
        elif i == 0 and null_counter == 1:
            result += '\n'
            null_counter = 0
            table_counter += 1

        elif players_counter == 0:
            player = await get_name_surname_on_telegram_id(telegram_id=i)
            result += f'{table_counter} - й Стол: {player} - '
            players_counter += 1
        elif players_counter == 1:
            player = await get_name_surname_on_telegram_id(telegram_id=i)
            result += f'{player}\n'
            table_counter += 1
            players_counter = 0

    await bot.edit_message_text(text=result,
                                chat_id=callback.from_user.id,
                                message_id=message_id,
                                reply_markup=get_back_button()
                                )


async def get_tournament_rating(callback: types.CallbackQuery) -> None:
    tournament_key = get_tournament_key_for_members(telegram_id=callback.from_user.id)
    result_string = buffer[tournament_key]['tournament_rating']

    await bot.edit_message_text(text=result_string,
                                message_id=callback.message.message_id,
                                chat_id=callback.from_user.id,
                                reply_markup=get_back_button())


def register_members_tournament_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(get_all_members_in_tournament,
                                       lambda callback_query: callback_query.data == "get_tournaments_members",
                                       state='*')
    dp.register_callback_query_handler(button_back_to_tournament_menu,
                                       lambda callback_query: callback_query.data == "back_to_menu",
                                       state="*")
    dp.register_callback_query_handler(add_game_in_tournament,
                                       lambda callback_query: callback_query.data == "add_game",
                                       state="*")
    dp.register_callback_query_handler(commit_game_to_database,
                                       lambda callback_query: callback_query.data[1:4] == " - ",
                                       state=MembersStates.commit_game_to_database)
    dp.register_callback_query_handler(get_online_scoreboard,
                                       lambda callback_query: callback_query.data == "get_online_games_on_tables",
                                       state="*")
    dp.register_callback_query_handler(get_tournament_rating,
                                       lambda callback_query: callback_query.data == "check_tournament_rating",
                                       state="*")
