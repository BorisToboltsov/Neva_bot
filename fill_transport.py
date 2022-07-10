import datetime

import settings
from common import date
from connect_gsheets import connect
from connect_telegram import bot
from keyboard_telegram import keyboard


def fill_transport(message, main_menu):
    """Заполнение таблицы по транспорту


    Заполняет столбцы F листов с месяцами из листа Гиды столбцы B,
    Делает проверку на заполнение столбцов B, D, E, K, L, M, N, P, Q, AA листа месяца на следующее число
    message: Сообщение из телеграмма
    key: Стартовая клавиатура
    """
    if message.text in date()[2].values():
        start_time = datetime.datetime.now()
        bot.send_message(message.chat.id, 'Заполнение таблицы по транспорту')
        sheet_guides = connect(settings.SHEET_TRANSPORT, 'Гиды', ['A', 'B', 'C'])[0]
        sheet_month, work_sheet_month = connect(settings.SHEET_TRANSPORT, message.text,
                                                ['B', 'D', 'E', 'K', 'L', 'M', 'N', 'P', 'Q'])
        not_sent = []
        sent = []
        position = []
        values = []
        for i in sheet_month:
            for j in i:  # j - month
                if j.label[0] == 'D':
                    for k in sheet_guides:
                        for v in k:  # v - guides
                            if j.value == v.value and v.label[0] == 'A':
                                if len(k) == 3:
                                    position.append(f'E{j.row}')
                                    values.append([[k[1].value]])
                                    if len(i) == 8 and i[0].value == str(date()[1]):
                                        sent.append(f'Строка: {j.label[1:]}, лист: {message.text}\n')
                                else:
                                    not_sent.append(f'Строка: {v.label[1:]}, лист: Гиды\n')
                                if len(i) != 9 and i[0].value == str(date()[1]):
                                    not_sent.append(f'Строка: {j.label[1:]}, лист: {message.text}\n')

        work_sheet_month.update_values_batch(position, values)

        for i in sent:
            not_sent.remove(i)
        if len(not_sent) != 0:
            bot.send_message(message.chat.id, f'СООБЩЕНИЯ НЕ БУДУТ ДОСТАВЛЕНЫ ЗАВТРА: \n{"".join(not_sent)}не '
                                              f'заполнено значение в одном из полей B, D, E, K, L, M, N, P, Q!')
        end_time = datetime.datetime.now()
        bot.send_message(message.chat.id, f'Заполнение окончено, время выполнения {end_time - start_time}',
                         reply_markup=main_menu)
    else:
        bot.reply_to(message, 'Здесь необходимо выбрать месяц, попробуйте еще раз', 
                     reply_markup=keyboard(date()[2].values()))
        bot.register_next_step_handler(message, fill_transport, main_menu)
