import datetime
import re

import settings
from common import date
from connect_gsheets import connect
from connect_telegram import bot
from menu_telegram import choice


def send_message(message):
    """Отправляет сообщение в телеграмм


        Отправляет сообщение пользователям, id телеграм берет из столбца С лист гиды, отправляет отчет
        Александру Вохмину
        message: Сообщение из телеграмма
        key: Стартовая клавиатура
    """
    if date()[0] in date()[2].values():
        start_time = datetime.datetime.now()
        bot.send_message(message, 'Отправка сообщений')
        sheet_guides = connect(settings.SHEET_TRANSPORT, 'Гиды', ['A', 'B', 'C'])[0]
        sheet_month, work_sheet_month = connect(settings.SHEET_TRANSPORT, date()[0],
                                                ['B', 'D', 'E', 'K', 'L', 'M', 'N', 'P', 'Q', 'AA'])

        incongruity = []
        shipped = []
        not_sent = []
        position = []
        values = []
        for i in sheet_month:
            for j in i:
                for k in sheet_guides:
                    for v in k:
                        if j.value == v.value and v.label[0] == 'A' and len(k) == 3 and len(i) == 9 and \
                                i[0].value == str(date()[1]):
                            try:
                                phone_number = "".join(re.findall(r'\d', i[8].value))
                                if len(phone_number) == 11:
                                    phone_number = f'+7{phone_number[1:]}'
                                elif len(phone_number) == 22:
                                    phone_number = f'+7{phone_number[1:11]} +7{phone_number[12:]}'
                                elif len(phone_number) == 33:
                                    phone_number = f'+7{phone_number[1:11]} +7{phone_number[12:22]} +7{phone_number[23:]}'
                                fio = "".join(re.findall(r'[\w*\s]', i[8].value))
                                fio = "".join(re.findall(r'\D', fio))
                                new_message = f'Гид: {v.value}\nДата: {i[0].value}\nВремя подачи: {i[3].value}\nМесто ' \
                                              f'подачи: {i[5].value}\nВремя окончания: {i[4].value}\nМесто окончания: ' \
                                              f'{i[6].value}\nГос номер: {i[7].value}\nФИО: {fio}\nТелефон:' \
                                              f' {phone_number}'
                                bot.send_message(k[2].value, new_message)
                                shipped.append(f'Доставлено - {v.value} {k[1].value} '
                                               f'{datetime.datetime.now().strftime("%d.%m.%y %H:%M")}'
                                               f'\n{new_message}\n\n')
                                position.append(f'AA{j.row}')
                                values.append([[f'Отправлено {datetime.datetime.now().strftime("%H:%M:%S")}']])
                            except Exception as e:
                                # print(e)
                                not_sent.append(f'НЕ ДОСТАВЛЕНО!!!! Невозможно начать чат с пользователем {v.value} id '
                                                f'{k[2].value} {datetime.datetime.now().strftime("%d.%m.%y %H:%M")}\n')
                        elif len(k) != 3 and i[0].value == str(date()[1]):
                            incongruity.append(f'Строка: {v.label[1:]}, лист: Гиды\n')
                        if len(i) != 9 and i[0].value == str(date()[1]):
                            if i[-1].label[0:2] != 'AA':
                                not_sent.append(f'НЕ ДОСТАВЛЕНО!!!! Строка: {j.label[1:]}, лист: {date()[0]} '
                                                f'не заполнено значение в одном из полей B, D, E, K, L, M, N, P, Q!\n')
        work_sheet_month.update_values_batch(position, values)
        if len(shipped) != 0:  # Отправка отчета!
            bot.send_message(settings.SENT_REPORT, f"{''.join(shipped)}")
        if len(not_sent) != 0:  # Отправка отчета!
            bot.send_message(settings.SENT_REPORT, f"{''.join(set(not_sent))}")
        if len(incongruity) != 0:  # Отправка отчета!
            bot.send_message(settings.SENT_REPORT, f"Не заполнены какие-то поля в таблице! \n"
                                                   f"{''.join(set(incongruity))}")
        end_time = datetime.datetime.now()
        bot.send_message(message, f'Отправка закончена, время выполнения {(end_time - start_time)}')
    else:
        bot.register_next_step_handler(message, choice)
