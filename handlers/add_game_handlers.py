from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from states.add_game_states import AddGameStates, AddScoreSetsStates

from database.add_game_db import get_rivals, get_first_player, insert_data_score, insert_full_data_score

from keyboards.add_game_keyboard import game_score_keyboard, get_sets_count_keyboard, get_choice_game_type


async def select_rival(message: types.Message, state=FSMContext) -> None:
    """
    Функция принимает сообщение и состояние.
    Получает player_id(UUID) пары игроков, добавляет в memory.storage.
    Отвечает сообщением, что оппонент определен...
    Меняет state >>> AddGameStates.select_input_game_type.set
    :param message:
    :param state:
    :returns: None
    """
    player_2 = await get_rivals(message.text)
    player_1 = await get_first_player(message.from_user.id)
    async with state.proxy() as game_data:
        game_data['player_1'] = player_1
        game_data['player_2'] = player_2

    await message.reply(text='Оппонент определен, теперь выберите тип добавления игры',
                        reply_markup=get_choice_game_type())
    await AddGameStates.select_input_game_type.set()

# Создание глобального буфера, где ключ - telegram_id пользователя, который добавляет матч.
# Исключительно для добавления матча в режиме: "advanced".
buffer_add_advanced_game = {}


async def callback_states_set(callback: types.CallbackQuery, state=FSMContext) -> None:
    """
    Функция принимает callback. В зависимости от него отправляет сообщение
    (быстрый / полный) тип добавления матча. Если тип ПОЛНЫЙ, то устанавливает
    state >>> AddGameStates.add_sets_score.set
    :param callback:
    :returns: None
    """
    if callback.data == 'gametype_fast':
        await AddGameStates.add_game_score.set()
        await callback.message.answer(text='Укажите счет матча',
                                      reply_markup=game_score_keyboard())
    elif callback.data == 'gametype_advanced':
        buffer_add_advanced_game[callback.from_user.id] = [None, 0, 0]
        await AddGameStates.add_sets_score.set()
        await callback.message.answer(text='Выберите формат матча',
                                      reply_markup=get_sets_count_keyboard())


async def add_score(message: types.Message, state=FSMContext) -> None:
    """
    Функция добавляет матч в базу данных, счет получает из message.text,
    далее записывается в memory.storage. После выходит из state.
    :param message:
    :param state:
    :returns: None
    """
    score_1 = int(message.text[0])
    score_2 = int(message.text[-1])
    async with state.proxy() as game_data:
        game_data['score_1'] = score_1
        game_data['score_2'] = score_2
        print(game_data)
        await insert_data_score(game_data)

    await state.finish()
    await message.reply(text='Матч успешно добавлен в базу данных!',
                        reply_markup=None)


async def insert_sets_score(callback: types.CallbackQuery) -> None:
    """
    Функция принимает callback. Записывает в буфер добавления матча тип матча(до 2, 3 или 4 сетов)
    Отвечает пользователю, что бы тот ввел счет первого сета.
    :param callback:
    :returns: None
    """
    buffer_add_advanced_game[callback.from_user.id][0] = int(callback.data[-1])

    await callback.message.answer(text='Введите счет 1 сета:')
    await AddScoreSetsStates.set_1.set()


async def add_set_score(message: types.Message, state=FSMContext) -> None:
    """
    Функция добавляет в MemoryStorage информацию по каждому сету(счет).
    Если отыграны все сеты, то записывает данные в БД, если же матч не завершен,
    то выводит сообщение для введения данных для следующего сета.
    :param message:
    :param state:
    :returns: None
    """
    list_score = message.text.split(sep='-')
    local_score_1 = int(list_score[0])
    local_score_2 = int(list_score[1])

    if local_score_1 > local_score_2:
        buffer_add_advanced_game[message.from_user.id][1] += 1
    else:
        buffer_add_advanced_game[message.from_user.id][2] += 1

    print(buffer_add_advanced_game[message.from_user.id])  # techincal info

    sets_number = buffer_add_advanced_game[message.from_user.id][1] + buffer_add_advanced_game[message.from_user.id][2]

    async with state.proxy() as game_data:
        game_data[f's1_{sets_number}'] = local_score_1
        game_data[f's2_{sets_number}'] = local_score_2
        game_data['score_1'] = buffer_add_advanced_game[message.from_user.id][1]
        game_data['score_2'] = buffer_add_advanced_game[message.from_user.id][2]
        print(game_data)

    if (
            game_data['score_1'] == buffer_add_advanced_game[message.from_user.id][0] or
            game_data['score_2'] == buffer_add_advanced_game[message.from_user.id][0]
    ):
        await state.finish()
        await insert_full_data_score(game_data, sets_count=sets_number)
        await message.answer('Матч успешно добавлен! ')
        buffer_add_advanced_game.pop(message.from_user.id)
    else:
        await message.answer(f'Введите счет {sets_number + 1} сета: ')


def register_add_game_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(select_rival, state=AddGameStates.select_rival)
    dp.register_message_handler(add_score, state=AddGameStates.add_game_score)
    dp.register_callback_query_handler(insert_sets_score,
                                       lambda callback_query: callback_query.data[0:4] == 'sets',
                                       state=AddGameStates.add_sets_score)
    dp.register_message_handler(add_set_score, state=AddScoreSetsStates.all_states)
    dp.register_callback_query_handler(callback_states_set,
                                       lambda callback_query: callback_query.data[0:8] == 'gametype',
                                       state=AddGameStates.select_input_game_type)
