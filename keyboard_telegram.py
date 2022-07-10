from telebot import types


def keyboard(key_names):
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in key_names:
        key.add(*[types.KeyboardButton(name) for name in [i]])
    return key
