import logging
import ssl
import datetime
import time
import threading
import pygsheets
import schedule
import settings
from aiohttp import web
import telebot
from telebot import types
import re

WEBHOOK_URL_BASE = "https://{}:{}".format(settings.WEBHOOK_HOST, settings.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(settings.TOKEN_TELEGRAM)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(settings.TOKEN_TELEGRAM)

app = web.Application()

# client = pygsheets.authorize(client_secret=settings.KEY_PATH)
client = pygsheets.authorize(client_secret=settings.KEY_CONSTANT, credentials_directory=settings.KEY_PATH)


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)


def date():
    """Даты"""
    list_month = {'January': 'Январь', 'February': 'Февраль', 'March': 'Март', 'April': 'Апрель',
                  'May': 'Май', 'June': 'Июнь', 'July': 'Июль', 'August': 'Август',
                  'September': 'Сентябрь', 'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'}
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    next_month_ru = list_month[tomorrow.strftime("%B")]
    tomorrow = tomorrow.strftime("%d.%m")

    return next_month_ru, tomorrow, list_month


def keyboard(key_names):
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in key_names:
        key.add(*[types.KeyboardButton(name) for name in [i]])
    return key


@bot.message_handler(commands=['help', 'start'])
def start_message(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, f'Ваш telegram_id - {message.from_user.id}')
        bot.register_next_step_handler(message, choice)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def choice(message):
    """Основное меню"""
    if str(message.from_user.id) in settings.ACCESS.values():
        main_menu = keyboard(
            ['Заполнить питание', 'Заполнить транспорт', 'Отправить сообщение', 'Показать мой telegram_id'])
    else:
        main_menu = keyboard(['Показать мой telegram_id'])
    if message.text == 'Заполнить питание' or 'Заполнить транспорт':
        if str(message.from_user.id) in settings.ACCESS.values():
            bot.send_message(message.chat.id, 'Выберите месяц', reply_markup=keyboard(date()[2].values()))
            if message.text == 'Заполнить питание':
                threading.Thread(bot.register_next_step_handler(message, fill_food, main_menu))
            else:
                threading.Thread(bot.register_next_step_handler(message, fill_transport, main_menu))
        else:
            bot.send_message(message.chat.id, f'У вас нет доступа, ваш telegram_id - {message.from_user.id}')

    elif message.text == 'Отправить сообщение':
        if str(message.from_user.id) in settings.ACCESS.values():
            threading.Thread(send_message(message.chat.id))
        else:
            bot.send_message(message.chat.id, f'У вас нет доступа, ваш telegram_id - {message.from_user.id}')
    elif message.text == 'Показать мой telegram_id':
        bot.send_message(message.chat.id, f'Ваш telegram_id - {message.from_user.id}', reply_markup=main_menu)
    else:
        bot.send_message(message.chat.id, 'Выберите что необходимо сделать', reply_markup=main_menu)


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
        bot.reply_to(message, 'Здесь необходимо выбрать месяц, попробуйте еще раз', reply_markup=main_menu)
        bot.register_next_step_handler(message, choice)


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
        # print(f"Доставлено {datetime.datetime.now().strftime('%H:%M:%S')}")
    else:
        bot.register_next_step_handler(message, choice)


def thr():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Отправка сообщения по заданному времени.
schedule.every().day.at(settings.SENDING_TIME).do(send_message, settings.SENT_REPORT)
# schedule.every(1).minutes.do(send_message, settings.SENT_REPORT)
threading.Thread(target=thr).start()

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(settings.WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(settings.WEBHOOK_SSL_CERT, settings.WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=settings.WEBHOOK_LISTEN,
    port=settings.WEBHOOK_PORT,
    ssl_context=context,
)
