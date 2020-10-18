import telebot
import config
import random
from telebot import types
import database as db
from categories import Categories

bot = telebot.TeleBot(config.API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('static/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)

    # keyboard underblock
    #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #category = types.KeyboardButton("Категории")
    #settings = types.KeyboardButton("Настройки")
    #statistic = types.KeyboardButton("Статистика")
    #markup.add(category, settings, statistic)

    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!\n Я - <b>СобакаБот</b>, созданный '
                                      'чтобы помочь вам отслеживать свое время в обучении! '
                     .format(message.from_user),
                     parse_mode='html')
    helper(message)


@bot.message_handler(commands=['help'])
def helper(message):
    bot.send_message(message.chat.id,"Сегодняшняя статистика: /today \n"
                     "За текущий месяц: /month \n"
                     "Последние внесённые записи: /expenses \n"
                     "Категории: /categories")


@bot.message_handler(commands=['categories'])
def categories_list(message):
    categories = Categories().get_all_categories()
    answer_message = "Категории:\n\n* " + \
                 ("\n* ".join([c.name + ' (' + ", ".join(c.aliases) + ')' for c in categories]))
    bot.send_message(message.chat.id, answer_message)



#@bot.message_handler(content_types=['text'])
#def myAnswer(message):
    #    if message.chat.type == 'private':
    #        if message.text == 'Категории':
    #            bot.send_message(message.chat.id, 'Здесь будет список категорий')
    #        elif message.text == 'Настройки':
    #
    #           markup = types.InlineKeyboardMarkup(row_width=2)
    #         item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
    #         item2 = types.InlineKeyboardButton("Не понравилось", callback_data='bad')
    #        markup.add(item1, item2)
    #        bot.send_message(message.chat.id, 'Здесь будут настройки', reply_markup=markup)


#@bot.callback_query_handler(func=lambda call: True)
#def callback_inline(call):
    #   try:
    #       if call.message:
    #          if call.data == 'good':
    #            bot.send_message(call.message.chat.id, 'Ты сделал правильный выбор')
    #        elif call.data == 'bad':
    #           bot.send_message(call.message.chat.id, 'Капец ты умник канечно')
    #
    #       bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message.id
    #                          , text='Категории',reply_markup=None)


    # except Exception as e:
#   print(repr(e))

bot.polling(none_stop=True)
