from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_choice_keyboard() -> ReplyKeyboardMarkup:
    choice_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_def = KeyboardButton(text='Защитный')
    button_att = KeyboardButton(text='Атакующий')
    choice_keyboard.add(button_def, button_att)

    return choice_keyboard
