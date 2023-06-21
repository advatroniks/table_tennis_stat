from aiogram import  Dispatcher, types, Bot
from bot.keyboards.tournaments_keyboards import *
from bot.states.tournament_states import TournamentStaes
from aiogram.dispatcher import FSMContext
from bot.database.add_game_db import get_rivals
from bot.database.tournaments_db import get_telegram_id, create_tournament, confirm_participation
from dotenv import load_dotenv
import os


load_dotenv('.env')
token = os.getenv("TOKEN_API")
bot = Bot(token)



async def select_tournament_type(callback: types.CallbackQuery) -> None:
    """
    Функция принимает коллбэк, меняет инлайн клавиатуру на выбор типа турнира
    """
    await callback.message.edit_text(text='Выберите тип турнира:')
    await callback.message.edit_reply_markup(reply_markup=get_select_tournament_keyboard())
    await TournamentStaes.insert_members_count_state.set()


async def get_members_counts_on_tournament(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Функция принимает коллбэк с типом турнира,
    выводит клавиатуру с выбором количества участников
    записывает в state_data id чата и сообщения с меню,
    для дальнейшей работы с этим сообщением
    """
    async with state.proxy() as tournament_data:
        tournament_data['menu_message_id'] = callback.message.message_id
        tournament_data['menu_chat_id'] = callback.message.chat.id
    await callback.message.edit_text(text='Выберите количество игроков:')
    await callback.message.edit_reply_markup(get_member_counts_keyboard())
    await TournamentStaes.insert_list_members_name_surname.set()


async def insert_inline_members(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Функция принимает коллбэк, состояние
    записывает в state_data количество участников,
    указывает ключ counter-счетчик ввода количества участников
    меняет состояние на цикл ввода игроков
    """
    tournament_id = await create_tournament(member_counts=int(callback.data[-1]))

    async with state.proxy() as tournament_data:
        tournament_data['counts_member'] = callback.data[-1]
        tournament_data['counter'] = 0
        tournament_data['list_members'] = 'Список участников:\n'
        tournament_data['confirm_list'] = []
        tournament_data['tournament_id'] = tournament_id


    await callback.message.edit_text('Теперь вводите ПО ОДНОМУ участнику турнира(Имя Фамилия)')
    await TournamentStaes.absolute_insert.set()


async def insert_member(message: types.Message, state: FSMContext) -> None:
    """
    функция принимает имя и фамилию игрока
    меняет сообщение , добавляя этого игрока в список участников турнира
    """
    member_telegram_id = await get_telegram_id(message.text)

    async with state.proxy() as tournament_data:
        counter = tournament_data['counter'] + 1
        tournament_data['list_members'] += message.text + '\n'
        tournament_data[f'member_{counter}'] = (message.text, member_telegram_id)
        tournament_data['counter'] += 1

    await message.delete()

    await bot.edit_message_text(chat_id=tournament_data['menu_chat_id'],
                                message_id=tournament_data['menu_message_id'],
                                text=tournament_data['list_members']
                                )

    if tournament_data['counts_member'] == str(tournament_data['counter']):

        await bot.edit_message_reply_markup(chat_id=tournament_data['menu_chat_id'],
                                    message_id=tournament_data['menu_message_id'],
                                    reply_markup=start_tournament_keyboard()
                                            )

        await TournamentStaes.confirm_member_state.set()
        for i in tournament_data:
            if i[0:6] == 'member':
                member_data = tournament_data[i]
                await bot.send_message(chat_id=member_data[-1],
                                       text='Вы добавлены для участия в турнире',
                                       reply_markup=get_confirm_include_tournament(tournament_data['tournament_id']))



async def confirm_members_process(state: FSMContext) -> None:
    data = await state.get_data()



async def get_tournament_process_menu(callback: types.CallbackQuery, state=FSMContext) -> None:
    await TournamentStaes.absolute_insert.set()
    tournament_id = callback.data[-36:]
    telegram_id = callback.from_user.id
    await confirm_participation(telegram_id=telegram_id, tournament_id=tournament_id)
    data = await state.get_data()
    print(data)
    await callback.message.edit_text(text='Вы подтвердили свое участие, ожидайте начала турнира!')
    print(data)





class TournamentTables():
    def __init__(self, table_counts:int, members:list):
        self.table_counts = table_counts
        self.members = members

    async def create_tournament(self):
        self.table_game_process = []
        for i in range(self.table_counts):
            self.table_game_process.append([i])


#
# async def insert_member_1(message: types.Message, state: FSMContext) -> None:
#     await Bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id)



def register_tournaments_handlers(dp:Dispatcher) -> None:
    dp.register_callback_query_handler(select_tournament_type,
                                       lambda callback_query: callback_query.data == 'add_tournament')
    dp.register_callback_query_handler(get_members_counts_on_tournament,
                                       lambda callback_query: callback_query.data[0:9] == 'tour_type',
                                       state=TournamentStaes.insert_members_count_state)
    dp.register_callback_query_handler(insert_inline_members,
                                       lambda callback_query: callback_query.data[0:5] == 'digit',
                                       state=TournamentStaes.insert_list_members_name_surname)
    dp.register_message_handler(insert_member, state=TournamentStaes.absolute_insert)
    dp.register_callback_query_handler(get_tournament_process_menu,
                                       lambda callback_query: callback_query.data[0:18] == 'confirm_tournament',
                                       state='*')
