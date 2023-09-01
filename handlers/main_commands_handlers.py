from aiogram import Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.states.registration_states import PlayerRegistrationState
from bot.states.add_game_states import AddGameStates
from bot.database.registration_db import check_registration_user
from bot.database.postgresql_connect import conn
from bot.keyboards.office_keyboard import main_office_keyboard, moderator_office_keyboard, administrator_office_keyboard
from aiogram.dispatcher import FSMContext
from bot.database.office_db import get_win_loses_statistics
from dotenv import load_dotenv
import os


storage = MemoryStorage()

load_dotenv('.env')
ADMIN = os.getenv('ADMIN')

HELP_COMMAND_STRING = '''
/start - начать работу с ботом
/help - вывести список команд
/reg_user - зарегистрироваться
/add_game - добавить игру
/cancel - отменить текущее действие
/description - описание бота 
/office - личный кабинет
'''


ADD_TYPE_GAME_INFORMATION = """
Выберите режим добавления игры:
*Быстрый - только итоговый счет
*Расширенный - указание счета в каждом сете
"""

async def cmd_start(message: types.Message) -> None:
    """
        Функция обрабатывает команду старт.
    """
    reply_text = ''' 
    Привет, %s!
    Что бы начать работу, изучи возможности бота
    /help
    ''' % message.from_user.first_name

    await message.answer(
        text=reply_text
    )


async def cmd_registration(message: types.Message) -> None:
    """ Функция обрабатывает команду регистрации и переводит State >> Registration """
    if await check_registration_user(message.from_user.id,conn.cursor()):
        await message.answer(text='Пожалуйста, введите ваше имя. ')
        await PlayerRegistrationState.reg_name.set()
    else:
        await message.answer('Вы уже зарегестрированны!')


async def cmd_cancel(message: types.Message, state=FSMContext) -> None:
    await message.reply(text='Операция прервана! ')
    await state.reset_data()
    data = await state.get_data()
    await state.finish()
    print(data)


async def cmd_description(message: types.Message) -> None:
    await message.answer('Описание работы бота')


async def cmd_help(message: types.Message) -> None:
    await message.reply(text=HELP_COMMAND_STRING)

async def cmd_add_game(message: types.Message) -> None:
    await message.answer('Введите Имя и Фамилию соперника! ')
    await AddGameStates.select_rival.set()


async def cmd_open_office(message: types.Message) -> None:
    if message.from_user.id == int(ADMIN):
        keyboard = administrator_office_keyboard(moderator_office_keyboard(main_office_keyboard()))
    else:
        keyboard = main_office_keyboard()

    text = await get_win_loses_statistics(callback=message)
    interim_str = ''
    list_emodji = '🏓✅❌'
    count = 0
    for i in text:
        interim_str += i + list_emodji[count]
        count += 1

    result_string = 'Личный кабинет:' + interim_str


    await message.answer(text=result_string,
                         reply_markup=keyboard)

89028066003
def registrate_main_commands(dp: Dispatcher) -> None:
    """
    Регистрация хендлеров комманд
    """

    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(cmd_registration, commands=['registration'])
    dp.register_message_handler(cmd_cancel, commands=['cancel'], state='*')
    dp.register_message_handler(cmd_description, commands=['description'])
    dp.register_message_handler(cmd_help, commands=['help'])
    dp.register_message_handler(cmd_add_game, commands=['add_game'])
    dp.register_message_handler(cmd_open_office,commands=['office'])
