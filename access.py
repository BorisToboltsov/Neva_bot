import settings
from connect_gsheets import connect
from connect_telegram import bot


def check_access(user_id):
    bot.send_message(user_id, f'Проверка доступа')
    sheet_access = connect(settings.SHEET_ACCESS, "Доступ",
                           ['A', 'B', 'C'])[0]

    full_access = {}
    sales_access = {}
    suppliers_access = {}
    for cell in sheet_access:
        if cell[2].value == "FULL_ACCESS":
            full_access[cell[1].value] = [cell[0].value, cell[2].value]
        elif cell[2].value == "SALES_ACCESS":
            sales_access[cell[1].value] = [cell[0].value, cell[2].value]
        elif cell[2].value == "SUPPLIERS_ACCESS":
            suppliers_access[cell[1].value] = [cell[0].value, cell[2].value]
    if str(user_id) in full_access:
        check = "FULL_ACCESS"
    elif str(user_id) in sales_access:
        check = "SALES_ACCESS"
    elif str(user_id) in suppliers_access:
        check = "SUPPLIERS_ACCESS"
    else:
        check = "NOT_ACCESS"
    return check
