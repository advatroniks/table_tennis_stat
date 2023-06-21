from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton



def main_office_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    statistic_btn = InlineKeyboardButton(text='Статистика',callback_data='statistics')
    last_games_btn = InlineKeyboardButton(text='Последние игры', callback_data='last_games')
    add_game_btn = InlineKeyboardButton(text='Добавить игру', callback_data='add_game')
    add_profile_photo = InlineKeyboardButton(text='Добавить фото профиля', callback_data='add_profile_photo')
    update_info_btn = InlineKeyboardButton(text='Обновить информацию', callback_data='update_info')
    select_player_for_rate = InlineKeyboardButton(text='Выбрать игрока для сравнения', callback_data='rate_player')

    keyboard.row(statistic_btn, last_games_btn)
    keyboard.row(select_player_for_rate)
    keyboard.row(add_game_btn)
    keyboard.row(add_profile_photo)
    keyboard.row(update_info_btn)

    return keyboard


def moderator_office_keyboard(keyboard:InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    add_tournament_button = InlineKeyboardButton(text='Добавить турнир', callback_data='add_tournament')
    keyboard.row(add_tournament_button)

    return keyboard

def administrator_office_keyboard(keyboard:InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    add_moderator_button = InlineKeyboardButton(text='Добавить модератора', callback_data='add_moderator')

    keyboard.row(add_moderator_button)

    return keyboard