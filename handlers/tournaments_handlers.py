import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.tournaments_keyboards import *
from states.tournament_states import TournamentStaes
from database.tournaments_db import *

from bot_instance import bot
from buffer import buffer

# Определяем в глобальной области видимости buffer для турнира.
# Подробное описание см.в файле buffer.py
buffer = buffer


def get_tournament_key_for_members(telegram_id: str) -> str:
    """
    Функция получает айди пользователя, проверяет, есть ли он в списке
    участников какого либо АКТИВНОГО турнира, если находит совпадение,
    то возвращает buffer[tournament_key] подробное описание buffer
    в файле buffer.py
    :param telegram_id:
    :return: buffer[tournament_key]
    """
    for i in buffer:
        if i.find(str(telegram_id)) != -1:
            return i
        else:
            print('bad news')


class Tournament:
    """
    Класс турнира. Создавая объект этого класса, вы создаете турнир.(стандартный круговой)
    В параметры экземпляра класса надо передать количество столов, а так же список участников
    При инициализации класса генерируются все матчи. А так же назначаются на все указанные столы
    пары игроков.

    Parameters
        table_counts - количество столов для проводимого турнира
        players - список участников турнира(tuple)

    Exceptions
        Если количество столов больше чем для одновременной игры всех участников
    """

    def __init__(self, table_counts: int, tournament_key: str):
        """
        Инициализатор класса. Принимает количество столов, и ключ турнира(buffer[tournament_key])
        Сверяет переданное количество столов с допустимым.
        Определяет атрибуты экземпляра(количество столов, список игроков, ключ турнира,
        генерирует все матчи турнира, так же распределяет первые матчи у данного турнира по столам)
        :param table_counts:
        :param tournament_key:
        :return: None
        """
        if table_counts * 2 > len(buffer[tournament_key]['tournament_members']):
            raise Exception('Tables > than players couples')
        self.table_counts = table_counts
        self.players = buffer[tournament_key]['tournament_members']
        self.tournament_key = tournament_key
        self.matches = self.generate_matches()
        self.table_conditions = self.add_first_matches_on_tables()

    def generate_matches(self):
        """
        Метод генерации всех матчей при инициализации
        :return: matches - список всех матчей(list)
        """
        matches = list()
        counter = 0
        for i in self.players:
            counter += 1
            for j in self.players[counter:]:
                matches.append((i, j))

        buffer[self.tournament_key]['game_counter'] = len(matches)
        return matches

    def add_first_matches_on_tables(self):
        """
        Метод, при инициализации объекта добавляет матчи на все
        столы, которые указаны для турнира.

        :return: Table_conditions - список пар игроков(list) каждые два объекта по порядку - пара игроков.
            Номер стола - индекс второго игрока из пары
        """
        tables_conditions = []
        counter = 0
        for i in self.matches:
            if counter >= self.table_counts:
                print(counter, self.table_counts)
                break
            if i[0] not in tables_conditions and i[1] not in tables_conditions:
                print('ok')
                tables_conditions.append(i[0])
                tables_conditions.append(i[1])
                counter += 1
                self.matches.remove(i)
        self.input_table_conditions = tables_conditions
        buffer[self.tournament_key]['table_conditions'] = tables_conditions
        buffer[self.tournament_key]['games'] = self.matches
        return tables_conditions

    async def start_tournament(self):
        """
        Метод стартует турнир, запускает цикл, который работает, пока
        есть ХОТЯ БЫ ОДНА предстоящая игра.

        :return:

        """

        # Главный цикл турнира, работает пока есть предстоящие матч,
        # проверяет каждые ДВЕ секунды, освободились ли столы.
        # Если есть свободный стол, то на него добавляется матч.
        while len(buffer[self.tournament_key]['games']) > 0:
            counter = 0
            await asyncio.sleep(2)
            if 0 in buffer[self.tournament_key]['table_conditions']:
                finished_table = buffer[self.tournament_key]['table_conditions'].index(0)

                # цикл, который обходит все матчи, если находит, что НИ ОДИН ИГРОК из пары
                # в данный момент не играет, то добавляет на стол, где только что завершилась
                # игра
                for i in buffer[self.tournament_key]['games']:
                    # Проверка, на то, что бы цикл не уходил в бесконечность.
                    # Если ни один предстоящий матч не соответствует условиям, цикл прекращается
                    if counter > len(buffer[self.tournament_key]['games']):
                        break

                    # Добавление матча на указанный выше стол, если успешно матч добавлен, то
                    # этот матч удаляется из списка предстоящих матчей и цикл завершается.
                    if i[0] not in self.table_conditions and i[1] not in buffer[self.tournament_key]['table_conditions']:
                        print('test', finished_table)
                        buffer[self.tournament_key]['table_conditions'][finished_table] = i[0]
                        buffer[self.tournament_key]['table_conditions'][finished_table + 1] = i[1]
                        buffer[self.tournament_key]['games'].remove(i)

                        # service_information
                        print('Game added! Success!!')

                        # Цикл, проходит по паре игроков, которые были ТОЛЬКО ЧТО добавлены
                        # на столы и меняет их турнирные сообщения на указание текущего матча.
                        for player in i:
                            rival, table = await get_rival_and_table_number(telegram_id=player)
                            name_surname_rival = await get_name_surname_on_telegram_id(telegram_id=rival)
                            await bot.edit_message_text(chat_id=player,
                                                        message_id=await get_message_id_in_active_tournament(
                                                            telegram_id=player),
                                                        text=f'Ваш соперник {name_surname_rival}, Номер стола:  {table}',
                                                        reply_markup=get_tournament_menu_keyboard(is_active_gamer=0)
                                                        )
                        break
                    counter += 1
            else:
                print('Not free tables!')

            # Блок, который отвечает за обновления рейтинга(учета очков в турнире).
            # Каждые 2 секунды идет проверка по значению выше.(await asyncio.sleep())
            tournament_id = buffer[self.tournament_key]['tournament_id']
            players_dictionary = await get_all_members_rating(tournament_id=tournament_id)
            result_string = ''
            current_list = []

            # Цикл обходит словарь, где ключ - telegram_id, score - список["имя фамилия", "message_id", "кол-во очков"]
            for player_name, score in players_dictionary.items():
                current_list.append([score[0], score[2]])

            # Присваивается в итоговый список отсортированный по убыванию очков current_list по ПЕРВОМУ ЭЛЕМЕНТУ,
            # то есть по очкам. Пример: [["Иван Иванов", 4], ["Василий Андреев", 7]]. Будет сортировка по 4 и 7.
            total_list = sorted(current_list, key=lambda x: x[1], reverse=True)
            for i in total_list:
                result_string += f'{i[0]} - {i[1]}\n'
            buffer[self.tournament_key]['tournament_rating'] = result_string

        while True:
            await asyncio.sleep(10)
            if buffer[self.tournament_key]['game_counter'] == 0:
                for member in buffer[self.tournament_key]['tournament_members']:
                    message_id = await get_message_id_in_active_tournament(telegram_id=member)
                    await bot.edit_message_text(text=f'Турнир окончен\n{result_string}',
                                                message_id=message_id,
                                                chat_id=member
                                                )
                await set_tournament_identification_offline(tournament_id=tournament_id)
                buffer.pop(self.tournament_key)
                print(buffer)
                break


async def select_tournament_type(callback: types.CallbackQuery) -> None:
    """
    Функция принимает callback, меняет inline keyboard на выбор типа турнира
    :param callback:
    :returns: None
    """
    await callback.message.edit_text(text='Выберите тип турнира:')
    await callback.message.edit_reply_markup(reply_markup=get_select_tournament_keyboard())
    await TournamentStaes.insert_members_count_state.set()


async def get_members_counts_on_tournament(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Функция принимает callback с типом турнира,
    выводит клавиатуру с выбором количества участников
    записывает в state_data и id чата и сообщения с меню,
    для дальнейшей работы с этим сообщением
    :param callback:
    :param state:
    :returns: None
    """
    async with state.proxy() as tournament_data:
        tournament_data['menu_message_id'] = callback.message.message_id
        tournament_data['menu_chat_id'] = callback.message.chat.id
    await callback.message.edit_text(text='Выберите количество игроков:')
    await callback.message.edit_reply_markup(get_member_counts_keyboard())
    await TournamentStaes.insert_list_members_name_surname.set()


async def insert_inline_members(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Функция принимает callback, state
    записывает в state_data количество участников,
    указывает ключ counter-счетчик ввода количества участников
    меняет состояние на цикл ввода игроков

    :param callback:
    :param state:
    :returns: None
    """
    tournament_id = await create_tournament(member_counts=int(callback.data[-1]))

    async with state.proxy() as tournament_data:
        tournament_data['counts_member'] = callback.data[-1]
        tournament_data['counter'] = 0
        tournament_data['list_members'] = 'Список участников:\n'
        tournament_data['confirm_list'] = []
        tournament_data['tournament_id'] = tournament_id
        tournament_data['tournament_key'] = '|'

    await callback.message.edit_text('Теперь вводите ПО ОДНОМУ участнику турнира(Имя Фамилия)')
    await TournamentStaes.absolute_insert.set()


async def insert_member(message: types.Message, state: FSMContext) -> None:
    """
    Функция принимает имя и фамилию игрока
    меняет сообщение, добавляя этого игрока в список участников турнира
    :param message:
    :param state:
    :returns: None
    """
    member_telegram_id = await get_telegram_id(message.text)

    async with state.proxy() as tournament_data:
        counter = tournament_data['counter'] + 1
        tournament_data['list_members'] += message.text + '\n'
        tournament_data[f'member_{counter}'] = (message.text, member_telegram_id)
        tournament_data['tournament_key'] += f'{member_telegram_id}' + '|'
        tournament_data['counter'] += 1

    await message.delete()

    await bot.edit_message_text(chat_id=tournament_data['menu_chat_id'],
                                message_id=tournament_data['menu_message_id'],
                                text=tournament_data['list_members']
                                )

    if tournament_data['counts_member'] == str(tournament_data['counter']):
        await set_active_tournament(tournament_data['tournament_id'])
        await TournamentStaes.confirm_member_state.set()
        for i in tournament_data:
            if i[0:6] == 'member':
                member_data = tournament_data[i]
                await bot.send_message(chat_id=member_data[-1],
                                       text=f'Вы добавлены для участия в турнире',
                                       reply_markup=get_confirm_include_tournament(
                                           tournament_id=tournament_data['tournament_id'])
                                       )
        # declared_members - ЗАЯВЛЕННЫЕ игроки, которые пока что не подтвердили участие.
        declared_members = tournament_data['list_members'].split(sep='\n')[1:-1]
        total_message = tournament_data['list_members']
        counter = 0
        while True:
            if len(declared_members) == 0:
                await bot.edit_message_text(text=total_message,
                                            chat_id=tournament_data['menu_chat_id'],
                                            message_id=tournament_data['menu_message_id'],
                                            reply_markup=start_tournament_keyboard()
                                            )
                break

            await asyncio.sleep(5)
            # Цикл, который каждые 5 секунд проверяет, подтвердил ли игрок свое участие в турнире,
            # если подтвердил, то он удаляется из ЗАЯВЛЕННЫХ ИГРОКОВ, ТАК КАК ОН ПОДТВЕРЖДЕННЫЙ игрок.
            for player in declared_members:
                telegram_id = await get_telegram_id(rival_name=player)
                tournament_id = tournament_data['tournament_id']
                counter = 0
                if await check_player_confirmed_tournament(telegram_id=telegram_id, tournament_id=tournament_id):
                    print(counter)
                    declared_members.remove(player)
                    total_message = total_message.replace(player, player + ' ✅')
                    await bot.edit_message_text(text=total_message,
                                                chat_id=tournament_data['menu_chat_id'],
                                                message_id=tournament_data['menu_message_id']
                                                )

            counter += 1


async def get_tournament_process_menu(callback: types.CallbackQuery) -> None:
    """
    Функция отрабатывает после подтверждения участия в турнире.
    Извлекает из callback.data ID турнира(UUID).
    Меняет сообщение участника. Записывает в БД(all_tournaments >> players_list)
     {"telegram_id": ["name_surname", "message_id"]}
    :param callback:
    :return:
    """
    await TournamentStaes.absolute_insert.set()

    result_list_callback_data = callback.data.split(sep='-----')
    tournament_id = result_list_callback_data[1]

    telegram_id = callback.from_user.id
    name_surname = await confirm_participation(telegram_id=telegram_id, tournament_id=tournament_id)
    await insert_members_message_id(telegram_id=telegram_id,
                                    message_id=callback.message.message_id,
                                    member_name=name_surname)

    await callback.message.edit_text(text='Вы подтвердили свое участие, ожидайте начала турнира!',
                                     reply_markup=get_tournament_menu_keyboard())


async def get_rival_and_table_number(telegram_id: str) -> tuple:
    """
    Функция, которая принимает на вход telegram_id.
    Возвращает кортеж(соперник, который В ДАННЫЙ МОМЕНТ ИГРАЕТ С юзером и номер стола)
    :param telegram_id:
    :return: Кортеж(соперник, номер стола)
    """
    rival = None
    table = None

    key_tournament = get_tournament_key_for_members(telegram_id=telegram_id)

    if telegram_id in buffer[key_tournament]["table_conditions"]:
        table_position = buffer[key_tournament]["table_conditions"].index(telegram_id)
        if table_position == 0:
            rival = buffer[key_tournament]["table_conditions"][1]
            table = 1
        elif table_position == 1:
            rival = buffer[key_tournament]["table_conditions"][0]
            table = 1
        elif table_position % 2 != 0:
            rival = buffer[key_tournament]["table_conditions"][table_position - 1]
            table = table_position - 1
        elif table_position % 2 == 0:
            rival = buffer[key_tournament]["table_conditions"][table_position + 1]
            table = table_position
    else:
        print('error')

    return rival, table


async def check_player_is_in_tournament(telegram_id: str) -> None:
    """
    Функция принимает telegram_id и проверяет, должен ли В ДАННЫЙ МОМЕНТ участник играть.
    Если игрок сейчас должен играть, то сообщение изменяется и указывает на оппонента и номер стола.
    Если же В ДАННЫЙ МОМЕНТ игрок не должен играть, сообщение изменяется и сообщает, что надо ожидать.
    :param telegram_id:
    :return: None
    """
    tournament_key = get_tournament_key_for_members(telegram_id=telegram_id)

    if telegram_id in buffer[tournament_key]['table_conditions']:
        rival, table = await get_rival_and_table_number(telegram_id=telegram_id)
        name_surname_rival = await get_name_surname_on_telegram_id(telegram_id=rival)
        await bot.edit_message_text(text=f'Ваш соперник {name_surname_rival}, Номер стола {table}',
                                    message_id=await get_message_id_in_active_tournament(telegram_id=telegram_id),
                                    chat_id=telegram_id,
                                    reply_markup=get_tournament_menu_keyboard(is_active_gamer=0)
                                    )
    else:
        await bot.edit_message_text(text='Ожидайте вашего матча!',
                                    message_id=await get_message_id_in_active_tournament(telegram_id=telegram_id),
                                    chat_id=telegram_id,
                                    reply_markup=get_tournament_menu_keyboard())


async def start_tournament(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Модератор турнира начинает турнир, функция принимаем объект callback(нажатие на кнопку начать турнир)
    функция из объекта state получает список игроков и их telegram_id, далее на этом основании формирует
    pull матчей.
    :param state:
    :param callback:
    :return: None
    """
    # Получаем данные из MemoryStorage создателя турнира.
    data = await state.get_data()

    # Делаем запрос в БД, по айди турнира получаем список всех telegram_id участников турнира.
    members_data = await get_telegram_id_message_id(data['tournament_id'])

    # Получаем ключ, для доступа через буфер в данные турнира
    tournament_key = data['tournament_key']

    # Добавляем в ключ турнира telegram_id создателя турнира, что бы на случай отмены удалить все данные из буфера.
    tournament_key += str(callback.from_user.id) + '|'

    buffer.update({tournament_key: None})
    players_tuple = tuple(members_data.keys())


    # создаем параметры для турнира
    buffer[tournament_key] = {
        "tournament_members": players_tuple,
        "table_conditions": None,
        "games": None,
        "name_surname_members": data['list_members'],
        "tournament_id": data['tournament_id'],
        "game_counter": None,
        "tournament_rating": None,
    }

    # Создаем объект класса Tournament.
    main_tournament = Tournament(table_counts=2,
                                 tournament_key=tournament_key)

    for i in buffer[tournament_key]['tournament_members']:
        await check_player_is_in_tournament(telegram_id=i)

    # Запускаем метод турнира, для его начала.
    await main_tournament.start_tournament()


def register_tournaments_handlers(dp: Dispatcher) -> None:
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
    dp.register_callback_query_handler(start_tournament,
                                       lambda callback_query: callback_query.data == 'start_tournament',
                                       state='*')
