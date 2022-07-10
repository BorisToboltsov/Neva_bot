import telebot
import settings
import logging


bot = telebot.TeleBot(settings.TOKEN_TELEGRAM)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
