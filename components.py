import telebot
from telebot import types

from resourses import config

bot = telebot.TeleBot(config.API_TOKEN)


def back_to_menu_inline_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅ назад в меню", callback_data='back_to_menu'))
    return markup
