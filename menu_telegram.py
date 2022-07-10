import settings
from keyboard_telegram import keyboard


def menu(user_id):
    """Основное меню"""
    if str(user_id) in settings.ACCESS.values():
        main_menu = keyboard(
            ['Заполнить питание', 'Заполнить транспорт', 'Отправить сообщение', 'Показать мой telegram_id'])
    else:
        main_menu = keyboard(['Показать мой telegram_id'])
    return main_menu
