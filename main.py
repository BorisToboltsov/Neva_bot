import ssl
import threading
import settings
import telebot
import schedule
from aiohttp import web

from common import date
from connect_telegram import bot
from fill_food import fill_food
from fill_transport import fill_transport
from keyboard_telegram import keyboard
from menu_telegram import menu
from send_message_client import send_message_client
from shedule import thr
from send_message import send_message

WEBHOOK_URL_BASE = f"https://{settings.WEBHOOK_HOST}:{settings.WEBHOOK_PORT}"
WEBHOOK_URL_PATH = f"/{settings.TOKEN_TELEGRAM}/"

app = web.Application()


@bot.message_handler(commands=['help', 'start'])
def start_message(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, f'Ваш telegram_id - {message.from_user.id}')
        bot.register_next_step_handler(message, choice)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def choice(message):
    main_menu = menu(message.from_user.id)
    if message.text == 'Заполнить питание' or message.text == 'Заполнить транспорт':
        if str(message.from_user.id) in settings.ACCESS.values():
            bot.send_message(message.chat.id, 'Выберите месяц', reply_markup=keyboard(date()[2].values()))
            if message.text == 'Заполнить питание':
                threading.Thread(bot.register_next_step_handler(message, fill_food, main_menu))
            else:
                threading.Thread(bot.register_next_step_handler(message, fill_transport, main_menu))
        else:
            bot.send_message(message.chat.id, f'У вас нет доступа, ваш telegram_id - {message.from_user.id}')
    elif message.text == 'Отправить сообщение, транспорт':
        if str(message.from_user.id) in settings.ACCESS.values():
            threading.Thread(send_message(message.chat.id))
        else:
            bot.send_message(message.chat.id, f'У вас нет доступа, ваш telegram_id - {message.from_user.id}')
    elif message.text == 'Отправить сообщение, клиенты':
        if str(message.from_user.id) in settings.ACCESS.values():
            threading.Thread(send_message_client())
        else:
            bot.send_message(message.chat.id, f'У вас нет доступа, ваш telegram_id - {message.from_user.id}')
    elif message.text == 'Показать мой telegram_id':
        bot.send_message(message.chat.id, f'Ваш telegram_id - {message.from_user.id}', reply_markup=main_menu)
    else:
        bot.send_message(message.chat.id, 'Выберите что необходимо сделать', reply_markup=main_menu)

 
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

# schedule.every(1).minutes.do(send_message, settings.SENT_REPORT)
# Set shedule
# Отправка сообщения по заданному времени.
schedule.every().day.at(settings.SENDING_TIME_TRANSPORT).do(send_message, settings.SENT_REPORT)
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
