import re
import datetime

import settings
from common import date
from connect_gsheets import connect
from connect_telegram import bot

"""
'D' - Название Экскурсии
'E' - Поставщик
'F' - Дата экскурсии
'G' - Место сбора
'H' - Фио туристов
'I' - Моб.номер
'J' - Кол-во туристов
'P' - Гид
'R' - Статус
"""


def send_message_client(user_id):
    bot.send_message(user_id, 'Отправка сообщений')
    start_time = datetime.datetime.now()
    sheet_excursions, work_sheet_excursions = connect(settings.SHEET_EXCURSIONS, "продажи 2022",
                                                      ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'P', 'R'])
    sheet_guides = connect(settings.SHEET_TRANSPORT, 'Гиды', ['A', 'B', 'C'])[0]

    not_sent = []
    sent = []
    position = []
    values = []
    for i in sheet_excursions:
        for j in i:
            if j.value == "Невские Сезоны":
                for k in i:
                    # if k.value == str(date()[1]):
                    #     if len(i) != 8:
                    #         not_sent.append(f'НЕ ДОСТАВЛЕНО!!!! Строка: {k.label[1:]},'
                    #                         f' не заполнено значение в одном из полей\n')
                    #     elif len(i) == 8 and i[-1].value[:10] != "Отправлено":
                    #         sent.append(i)
                    for guid in sheet_guides:
                        for cell in guid:
                            if cell.value == k.value and len(guid) == 3 and len(i) == 8 and i[-1].value[:10] != "Отправлено":
                                try:
                                    phone_number = "".join(re.findall(r'\d', i[5].value))
                                    if len(phone_number) == 11:
                                        phone_number = f'+7{phone_number[1:]}'
                                    new_message = f"""Гид: {cell.
                                    value}\nДата экскурсии: {i[2].
                                    value}\nНазвание экскурсии: {i[0].
                                    value}\nМесто сбора: {i[3].
                                    value}\nФИО туристов: {i[4].
                                    value}\nМобильный номер: {phone_number}\nКол-во туристов: {i[6].
                                    value}"""
                                    bot.send_message(guid[2].value, new_message)
                                    position.append(f'R{k.row}')
                                    values.append([[f'Отправлено {datetime.datetime.now().strftime("%H:%M:%S")}']])
                                except Exception:
                                    not_sent.append(f'НЕ ДОСТАВЛЕНО!!!! Невозможно начать чат с пользователем {cell.value}'
                                                    f' id {guid[2].value} '
                                                    f'{datetime.datetime.now().strftime("%d.%m.%y %H:%M")}\n')
                            elif len(guid) != 3:
                                not_sent.append(f'Строка: {cell.label[1:]}, лист: Гиды. Не все поля заполнены\n')
                            elif len(i) != 8:
                                not_sent.append(f'НЕ ДОСТАВЛЕНО!!!! Строка: {k.label[1:]},'
                                                f' не заполнено значение в одном из полей\n')
    bot.send_message(user_id, not_sent)
    work_sheet_excursions.update_values_batch(position, values)
    end_time = datetime.datetime.now()
    bot.send_message(user_id, f'Отправка закончена, время выполнения {(end_time - start_time)}')
