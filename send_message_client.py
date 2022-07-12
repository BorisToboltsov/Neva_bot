import re
import datetime

import settings
from common import date
from connect_gsheets import connect
from connect_telegram import bot

"""
'E' - Название Экскурсии
'F' - Поставщик
'G' - Дата экскурсии
'H' - Место сбора
'I' - Фио туристов
'J' - Моб.номер
'K' - Кол-во туристов
'Q' - Гид
'S' - Статус
"""


def send_message_client(user_id):
    bot.send_message(user_id, 'Отправка сообщений')
    # print('Отправка сообщений')
    start_time = datetime.datetime.now()
    sheet_excursions, work_sheet_excursions = connect(settings.SHEET_EXCURSIONS, "продажи 2022",
                                                      ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'Q', 'S'])
    sheet_guides = connect(settings.SHEET_TRANSPORT, 'Гиды', ['A', 'B', 'C'])[0]

    not_sent = []
    sent = []
    position = []
    values = []
    for i in sheet_excursions:
        for j in i:
            if j.value == "Невские Сезоны":
                for k in i:
                    for guid in sheet_guides:
                        for cell in guid:
                            if (cell.value == k.value and len(guid) == 3 and len(i) == 8 and i[-1].value[:10] != "Отправлено" and i[2].value == str(date()[1])) or \
                               (cell.value == k.value and len(guid) == 3 and len(i) == 8 and i[-1].value[:10] != "Отправлено" and i[2].value == str(date()[3])):
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
                                    bot.send_message(user_id, f'ДОСТАВЛЕНО:\n{new_message}')
                                    # print(new_message)
                                    position.append(f'S{k.row}')
                                    values.append([[f'Отправлено {datetime.datetime.now().strftime("%H:%M:%S")}']])
                                except Exception:
                                    not_sent.append(f'НЕ ДОСТАВЛЕНО!!!! Невозможно начать чат с пользователем {cell.value}'
                                                    f' id {guid[2].value} '
                                                    f'{datetime.datetime.now().strftime("%d.%m.%y %H:%M")}\n')
                            elif len(guid) != 3:
                                not_sent.append(f'Строка: {cell.label[1:]}, лист: Гиды. Не все поля заполнены\n')
                            if len(i) != 8 and k.value == str(date()[1]):
                                if i[-1].label[0:1] != "S":
                                    context = f'НЕ ДОСТАВЛЕНО!!!! Строка: {k.label[1:]},' \
                                              f' не заполнено значение в одном из полей\n'
                                    if context not in not_sent:
                                        not_sent.append(context)
    if len(not_sent) != 0:
        bot.send_message(user_id, not_sent)
        # print(not_sent)
    work_sheet_excursions.update_values_batch(position, values)
    end_time = datetime.datetime.now()
    bot.send_message(user_id, f'Отправка закончена, время выполнения {(end_time - start_time)}')
#     print(f'Отправка закончена, время выполнения {(end_time - start_time)}')
# send_message_client(12)
