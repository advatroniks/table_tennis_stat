from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_select_tournament_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    type_1 = InlineKeyboardButton(text='Круговая(каждый с каждым)',
                                  callback_data='tour_type_round_everyone')
    type_2 = InlineKeyboardButton(text='Круговая(в два круга)',
                                  callback_data='tour_type_twice_round_everyone')

    keyboard.add(type_1)
    keyboard.add(type_2)

    return keyboard

def get_member_counts_keyboard() -> None:
    keyboard = InlineKeyboardMarkup(row_width=4)

    for i in range(48):
        i += 1
        if i % 2 == 0:
            buttun = InlineKeyboardButton(text=str(i), callback_data='digit' + str(i))
            keyboard.insert(buttun)
        else:
            pass


    return keyboard


def get_confirm_include_tournament(tournament_id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text='Подтверждаю', callback_data=f'confirm_tournament_{tournament_id}')
    button_2 = InlineKeyboardButton(text='Отклоняю', callback_data='reject_tournament')

    keyboard.row(button_1, button_2)

    return keyboard


def get_main_tournament_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text='Список текущих игр', callback_data='main_menu_gamelist')
    button_2 = InlineKeyboardButton(text='Турнирная таблица', callback_data='main_menu_tour_table')
    button_3 = InlineKeyboardButton(text='Список участников турнира', callback_data='main_menu_members')
    button_4 = InlineKeyboardButton(text='Мой текущий матч', callback_data='main_menu_livegame')


def start_tournament_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text='Начать турнир', callback_data='start_tournament')
    button_2 = InlineKeyboardButton(text='Отменить турнир', callback_data='cancel_tournament')

    keyboard.add(button_1, button_2)

    return keyboard
