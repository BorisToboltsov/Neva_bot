from pathlib import Path

import settings
import pygsheets

# client = pygsheets.authorize(client_secret=settings.KEY_PATH)
# dir_path = Path.cwd()
# path = Path(dir_path, settings.KEY_CONSTANT)
#
# client = pygsheets.authorize(client_secret=path, credentials_directory=dir_path)
client = pygsheets.authorize(client_secret=settings.KEY_CONSTANT, credentials_directory=settings.KEY_PATH)


def connect(sheet, worksheet, columns):
    """ Получение данных из таблицы

    :param sheet: Питание - settings.SHEET_FOOD. Транспорт - settings.SHEET_TRANSPORT
    :param worksheet: Питание, транспорт - message.text. Сообщение - date()[0]
    :param columns: Питание - ['E', 'F', 'G', 'H'], ['H', 'I', 'J', 'Q'].
                    Транспорт, сообщения ['A', 'B', 'C'], ['B', 'D', 'E', 'K', 'M', 'P', 'Q', 'AA']
    :return:
    """
    sheet_food = client.open(sheet)

    work_sheet_data = sheet_food.worksheet('title', worksheet)
    work_sheet = work_sheet_data.get_all_values(returnas='cell', majdim='ROWS')
    work_sheet = [[j for j in i if j.value != '' and j.label[0] in columns or j.value != '' and j.label[0:2] in columns]
                  for i in work_sheet if i[0].value != '']
    for i in work_sheet:
        if not i:
            work_sheet.remove(i)
    return work_sheet, work_sheet_data
