from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext

from database.add_game_db import get_rivals, get_first_player
from database.office_db import *

from states.add_game_states import AddGameStates
from states.office_states import OfficeStates


async def get_correct_last_game_data(iter_obj: tuple) -> str:
    """
    Функция принимате кортеж:
    (Имя Фамилия 1 игрока, счет первого игрока, счет второго игрока, Имя Фамилия 2 игрока)
    Функция Приводит данные к виду: Фамилия И: 3-0 :Фамилия
    Возвращает результирующую строку
    :param iter_obj:
    :returns: Результирующая строка вида Фамилия И: 3-0 :Фамилия
    """

    first_player_list = iter_obj[0].split()
    first_player = first_player_list[1].capitalize() + ' ' + first_player_list[0][0].upper()
    second_player_list = iter_obj[3].split()
    second_player = second_player_list[1].capitalize() + ' ' + second_player_list[0][0].upper()
    first_score = str(iter_obj[1])
    second_score = str(iter_obj[2])
    data = str(iter_obj[4])
    result_string = first_player + ': ' + first_score + '-' + second_score + ' :' + second_player + ' ' + data

    return result_string


async def get_full_statistics(callback: types.CallbackQuery) -> None:
    """
    Функция получает на вход объект callback,
    Функция в переменную data сохраняет список всех игр
    На выходе функция выводит пользователю список всех игр,
    Отформатированного к результату get_correct_last_game_data
    :param callback:
    :returns: None
    """
    data = await get_last_10_games(callback=callback)
    result_string = ''
    print(data)
    for i in data:
        non_permanent_string = await get_correct_last_game_data(i)
        result_string += non_permanent_string + '\n'

    print(result_string)
    await callback.message.answer(text=result_string)


async def get_win_lose_counts(callback: types.CallbackQuery) -> None:
    """
    Функция принимает callback, после в data сохраняется кортеж,
    (кол-во игр, кол-во побед, кол-во поражений)
    Функция обрабатывает эти данные и приводит к виду результирующей строки
    для ответа клиенту.
    :param callback:
    :returns: None
    """
    data = await get_win_loses_statistics(callback=callback)
    result_string = ' Всего игр: %s \nПобед: %s \nПоражений: %s' % data
    print(result_string)
    await callback.message.answer(text=result_string)


async def insert_data_game(callback: types.CallbackQuery) -> None:
    await callback.message.answer('Введите Имя и Фамилию соперника! ')
    await AddGameStates.select_rival.set()


async def insert_player_for_rate(callback: types.CallbackQuery) -> None:
    await callback.message.answer('Введите Имя и Фамилию игрока для сравения: ')
    await OfficeStates.get_player_for_rate.set()


async def get_player_data_for_rate(message: types.Message, state: FSMContext) -> None:
    """
    Функция принимает message, state
    Функция получает id авторизованного игрока, id игрока для сравнения.
    Выводит клиенту личную статистику игрока для сравнения,
    Далее выводит игроку статистику очных встреч,
    После выводит Результаты и даты игр.
    :param message:
    :param state:
    :returns: None
    """

    self_player = await get_first_player(message.from_user.id)
    player_id_for_rate = await get_rivals(message.text)

    data = await get_personal_games(player_id_for_rate, self_player)
    personal_statistic = await get_personal_counter_win_lose(self_player, player_id_for_rate)

    result = await get_lose_win_rate_player(player_id_for_rate)  # личная статистика сравниваемого игрокаа
    player_name = message.text + '\n'
    result_string = player_name + 'Всего игр: %s \nПобед: %s \nПоражений: %s \nЛичные встречи:\n' % result
    total_string = ''.join(map(str, personal_statistic))
    emodji = '🏓✅❌'
    total_string = ''.join([c1 + c2 for c1, c2 in zip(total_string, emodji)])

    result_string += total_string + '\n'

    for i in data:
        non_permanent_string = await get_correct_last_game_data(i)
        result_string += non_permanent_string + '\n'

    await state.finish()
    await message.answer(result_string)


def register_office_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(get_full_statistics, lambda callback_query: callback_query.data == 'last_games')
    dp.register_callback_query_handler(get_win_lose_counts, lambda callback_query: callback_query.data == 'statistics')
    dp.register_callback_query_handler(insert_data_game, lambda callback_query: callback_query.data == 'addgame')
    dp.register_callback_query_handler(insert_player_for_rate, lambda callback_query: callback_query.data == 'rate_player')
    dp.register_message_handler(get_player_data_for_rate, state=OfficeStates.get_player_for_rate)