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


def get_member_counts_keyboard() -> InlineKeyboardMarkup:
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
    button_1 = InlineKeyboardButton(
        text='Подтверждаю',
        callback_data=f'confirm_tournament-----{tournament_id}')
    button_2 = InlineKeyboardButton(text='Отклоняю', callback_data='reject_tournament')

    keyboard.row(button_1, button_2)

    return keyboard


def start_tournament_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text='Начать турнир', callback_data='start_tournament')
    button_2 = InlineKeyboardButton(text='Отменить турнир', callback_data='cancel_tournament')

    keyboard.add(button_1, button_2)

    return keyboard


def get_tournament_menu_keyboard(is_active_gamer=1) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text='Участники Турнира', callback_data='get_tournaments_members')
    button_2 = InlineKeyboardButton(text='Текущие игры', callback_data='get_online_games_on_tables')
    button_3 = InlineKeyboardButton(text='Просмотреть текущие очки:', callback_data='check_tournament_rating')
    button_4 = InlineKeyboardButton(text='Указать счет матча', callback_data='add_game')

    keyboard.row(button_1, button_2)
    keyboard.row(button_3)

    if is_active_gamer != 1:
        keyboard.add(button_4)

    return keyboard


def get_back_button() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text='Назад', callback_data='back_to_menu')

    keyboard.add(button_1)

    return keyboard
