from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def add_game_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for i in range(3):
        score = f'3 - {i}'
        button_win = InlineKeyboardButton(text=score,
                                          callback_data=score)
        button_lose = InlineKeyboardButton(text=score[::-1],
                                           callback_data=score[::-1])
        keyboard.row(button_win, button_lose)

    button_back = InlineKeyboardButton(text='Назад',
                                       callback_data='back_to_menu')

    keyboard.row(button_back)

    return keyboard



