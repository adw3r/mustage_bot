from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Получить отчет")],
            [KeyboardButton(text="Добавить расход")],
            [KeyboardButton(text="Удалить расход")],
            [KeyboardButton(text="Изменить расход")],
        ],
        resize_keyboard=True
    )


def back_to_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад в меню")]], resize_keyboard=True
    )
