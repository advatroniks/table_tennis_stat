from uuid import UUID

from aiogram import types, Dispatcher
from states.registration_states import PlayerRegistrationState
from aiogram.dispatcher import FSMContext
import datetime
from database.registration_db import record_data, conn
from keyboards.registration_keyboards import get_choice_keyboard

async def check_handler(message: types.Message) -> None:
    await message.reply('Пожалуйства, введите корректные данные!')


check_name_surname = lambda message: not message.text.isalpha()
check_age = lambda message: not message.text.isdigit()
check_age_range = lambda message: not (90 > int(message.text) > 3)
check_game_style = lambda message: not message.text.lower() in ['атакующий', 'защитный']


async def set_name_player(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as reg_data:
        reg_data['name'] = message.text.lower()

    await message.reply(text='Отлично, теперь введите свою фамилию! ')
    await PlayerRegistrationState.reg_surname.set()


async def set_surname_player(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as reg_data:
        reg_data['surname'] = message.text.lower()

    await message.answer(text='Введите ваш возраст ')
    await PlayerRegistrationState.reg_age.set()


async def set_age_player(message: types.Message, state: FSMContext) -> None:
    birthday = datetime.date.today() - datetime.timedelta(365 * int(message.text))
    async with state.proxy() as reg_data:
        reg_data['birthday'] = birthday

    await message.answer(text='Ведите ваш город ')
    await PlayerRegistrationState.reg_city.set()


async def set_city_player(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as reg_data:
        reg_data['city'] = message.text.lower()

    await message.answer(text='Выберите ваш стиль игры:',
                         reply_markup=get_choice_keyboard())
    await PlayerRegistrationState.reg_game_style.set()


async def set_game_style(message: types.Message, state: FSMContext) -> None:
    if message.text.lower() == 'атакующий':
        game_style = True
    else:
        game_style = False
    async with state.proxy() as reg_data:
        reg_data['game_style'] = game_style
        reg_data['telegram_id'] = message.from_user.id
        await record_data(reg_data, conn.cursor())
        print(reg_data)
    await message.answer(text='Регистрация успешно завершена!')
    await state.finish()


def registser_user_handlers(dp: Dispatcher) -> None:
    '''
    Register user handlers
    '''
    dp.register_message_handler(check_handler, check_name_surname, state=PlayerRegistrationState.reg_name)
    dp.register_message_handler(set_name_player, state=PlayerRegistrationState.reg_name)

    dp.register_message_handler(check_handler, check_name_surname, state=PlayerRegistrationState.reg_surname)
    dp.register_message_handler(set_surname_player, state=PlayerRegistrationState.reg_surname)

    dp.register_message_handler(check_handler, check_age, state=PlayerRegistrationState.reg_age)
    dp.register_message_handler(check_handler, check_age_range, state=PlayerRegistrationState.reg_age)
    dp.register_message_handler(set_age_player, state=PlayerRegistrationState.reg_age)

    dp.register_message_handler(check_handler, check_name_surname, state=PlayerRegistrationState.reg_city)
    dp.register_message_handler(set_city_player, state=PlayerRegistrationState.reg_city)

    dp.register_message_handler(check_handler, check_game_style, state=PlayerRegistrationState.reg_game_style)
    dp.register_message_handler(set_game_style, state=PlayerRegistrationState.reg_game_style)
