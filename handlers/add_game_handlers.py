from aiogram import Dispatcher, types
from states.add_game_states import AddGameStates, AddScoreSetsStates
from aiogram.dispatcher import FSMContext
from database.add_game_db import get_rivals, get_first_player, insert_data_score, insert_full_data_score
from keyboards.add_game_keyboard import game_score_keyboard, get_sets_count_keyboard, get_choice_game_type


async def select_rival(message: types.Message, state=FSMContext) -> None:
    player_2 = await get_rivals(message.text)
    player_1 = await get_first_player(message.from_user.id)
    async with state.proxy() as game_data:
        game_data['player_1'] = player_1
        game_data['player_2'] = player_2

    await message.reply(text='Оппонент определен, теперь выберите тип добавления игры',
                        reply_markup=get_choice_game_type())
    await AddGameStates.select_input_game_type.set()


async def callback_states_set(callback: types.CallbackQuery, state = FSMContext) -> None:
    if callback.data == 'gametype_fast':
        await AddGameStates.add_game_score.set()
        await callback.message.answer(text='Укажите счет матча',
                                      reply_markup=game_score_keyboard())
    if callback.data == 'gametype_advanced':
        await AddGameStates.add_sets_score.set()
        await callback.message.answer(text='Выберите формат матча',
                                      reply_markup=get_sets_count_keyboard())


async def add_score(message: types.Message, state=FSMContext) -> None:
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


async def add_full_score(message: types.Message, state=FSMContext) -> None:
    await message.reply(text='Выберите формат матча:',
                        reply_markup=get_sets_count_keyboard())

    await AddGameStates.add_sets_score.set()


total_sets = None
score_1 = 0
score_2 = 0


async def insert_sets_score(callback: types.CallbackQuery, state=FSMContext) -> int:
    global total_sets
    await callback.message.answer(text='Введите счет 1 сета:')
    total_sets = int(callback.data[-1])
    await AddScoreSetsStates.set_1.set()


async def add_set_score(message: types.Message, state=FSMContext):
    global total_sets, score_1, score_2

    list_scorese = message.text.split(sep='-')
    local_score_1 = int(list_scorese[0])
    local_score_2 = int(list_scorese[1])


    if local_score_1 > local_score_2:
        score_1 += 1
    else:
        score_2 += 1
    print(score_1, score_2, total_sets) #techincal info
    sets_number = score_1 + score_2

    async with state.proxy() as game_data:
        game_data[f's1_{sets_number}'] = local_score_1
        game_data[f's2_{sets_number}'] = local_score_2
        game_data['score_1'] = score_1
        game_data['score_2'] = score_2
        print(game_data)

    if score_1 == total_sets or score_2 == total_sets:
        await state.finish()
        await insert_full_data_score(game_data, sets_count=sets_number)
        await message.answer('Матч успешно добавлен! ')
        score_1, score_2, total_sets = 0, 0, 0
    else:
        await message.answer(f'Введите счет {sets_number + 1} сета: ')






states_list = [AddScoreSetsStates.all_states]
def register_add_game_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(select_rival, state=AddGameStates.select_rival)
    dp.register_message_handler(add_score, state=AddGameStates.add_game_score)
    dp.register_message_handler(add_full_score, state=AddGameStates.select_type_game)
    dp.register_callback_query_handler(insert_sets_score,
                                       lambda callback_query: callback_query.data[0:4] == 'sets',
                                       state=AddGameStates.add_sets_score)
    dp.register_message_handler(add_set_score, state=AddScoreSetsStates.all_states)
    dp.register_callback_query_handler(callback_states_set,
                                       lambda callback_query: callback_query.data[0:8] == 'gametype',
                                       state=AddGameStates.select_input_game_type)
