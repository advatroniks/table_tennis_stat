from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def game_score_keyboard() -> ReplyKeyboardMarkup:
    game_score_key = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(3):
        score = f'3-{i}'
        button_win = KeyboardButton(text=score)
        button_lose = KeyboardButton(text=score[::-1])
        game_score_key.add(button_win, button_lose
                           )
    return game_score_key


def get_sets_count_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    two_sets = InlineKeyboardButton(text='2 сета', callback_data='sets_2')
    three_sets = InlineKeyboardButton(text='3 сета', callback_data='sets_3')
    four_sets = InlineKeyboardButton(text='4 сета', callback_data='sets_4')
    keyboard.add(three_sets)
    keyboard.row(two_sets, four_sets)

    return keyboard


def get_choice_game_type() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_fast = InlineKeyboardButton(text='Быстрый', callback_data='gametype_fast')
    button_advanced = InlineKeyboardButton(text='Расширенный', callback_data='gametype_advanced')
    keyboard.row(button_fast, button_advanced)

    return keyboard