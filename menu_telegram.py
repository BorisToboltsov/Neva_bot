import settings
import threading
from common import date
from connect_telegram import bot
from fill_food import fill_food
from fill_transport import fill_transport
from keyboard_telegram import keyboard
from send_message import send_message


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
