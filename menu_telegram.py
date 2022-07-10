import settings
from keyboard_telegram import keyboard
from access import check_access


def menu(user_id):
    """Основное меню"""
    check = check_access(user_id)
    print(check)
    if check == "FULL_ACCESS":
        main_menu = keyboard(
            ['Заполнить питание', 'Заполнить транспорт', 'Отправить сообщение, транспорт',
             'Отправить сообщение, туристы', 'Показать мой telegram_id'])
    elif check == "SALES_ACCESS":
        main_menu = keyboard(
            ['Отправить сообщение, туристы', 'Показать мой telegram_id'])
    elif check == "SUPPLIERS_ACCESS":
        main_menu = keyboard(
            ['Заполнить питание', 'Заполнить транспорт', 'Отправить сообщение, транспорт',
             'Показать мой telegram_id'])
    else:
        main_menu = keyboard(['Показать мой telegram_id'])
    return main_menu
