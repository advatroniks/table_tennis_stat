from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_choice_type_game() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = KeyboardButton(text='Простой')
    button_2 = KeyboardButton(text='Подробный')
    keyboard.add(button_1, button_2)

    return keyboard

