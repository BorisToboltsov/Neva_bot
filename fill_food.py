import datetime

import settings
from common import date
from connect_gsheets import connect
from connect_telegram import bot
from menu_telegram import choice


def fill_food(message, main_menu):
    """Заполнение таблицы по питанию


    Заполняет столбцы H, I, J, Q листов с месяцами из листа Реестр столбцы E, F, G, H
    message: Сообщение из телеграмма
    key: Стартовая клавиатура
    """
    if message.text in date()[2].values():
        start_time = datetime.datetime.now()

        bot.send_message(message.chat.id, 'Заполнение таблицы по питанию')

        sheet_registry = connect(settings.SHEET_FOOD, 'Реестр', ['E', 'F', 'G', 'H'])[0]
        sheet_month, work_sheet_month = connect(settings.SHEET_FOOD, message.text, ['H', 'I', 'J', 'Q'])

        lost = []
        position = []
        values = []
        for i in sheet_month:
            for j in i:
                if j.label[0] == 'H':
                    for k in sheet_registry:
                        for v in k:
                            if j.value == v.value and v.label[0] == 'E':
                                if len(k) == 4:
                                    # work_sheet_month.update_values_batch([f'I{j.row}', f'J{j.row}', f'Q{j.row}'],
                                    # [[[k[2].value]], [[k[3].value]], [[k[1].value]]])
                                    position.append(f'I{j.row}')
                                    position.append(f'J{j.row}')
                                    position.append(f'Q{j.row}')
                                    values.append([[k[2].value]])
                                    values.append([[k[3].value]])
                                    values.append([[k[1].value]])
                                else:
                                    lost.append(f'Строка: {v.label[1:]}, лист: Реестр\n')
        work_sheet_month.update_values_batch(position, values)
        if len(lost) != 0:
            bot.send_message(message.chat.id, f"Строки: \n{''.join(set(lost))} не соответствует шаблону!")
        end_time = datetime.datetime.now()
        bot.send_message(message.chat.id, f'Заполнение окончено, время выполнения {end_time - start_time}',
                         reply_markup=main_menu)
    else:
        bot.reply_to(message, 'Здесь необходимо выбрать месяц, попробуйте еще раз', reply_markup=main_menu)
        bot.register_next_step_handler(message, choice)
