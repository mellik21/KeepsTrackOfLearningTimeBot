from sqlite3 import IntegrityError

import telebot
import config
import random
from telebot import types
import database as db
from records import Records as records
from categories import Categories

bot = telebot.TeleBot(config.API_TOKEN)


@bot.message_handler(commands=['start'])
def menu(message):
    sti = open('static/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!\n Я - <b>СобакаБот</b>, созданный '
                                      'чтобы помочь вам отслеживать свое время в обучении! '
                     .format(message.from_user),
                     parse_mode='html')
    helper(message)


@bot.message_handler(commands=['help'])
def helper(message):
    bot.send_message(message.chat.id,
                     "Последние записи: /cases \n"
                     "Добавить категорию: /add_category\n"
                     "Категории: /categories")


@bot.message_handler(commands=['add_category'])
def add_category_header(message):
    msg = bot.send_message(message.chat.id,
                           'Введите кодовое название, полное название и псевдонимы категории через ; ')
    bot.register_next_step_handler(msg, add_category_to_db)


def add_category_to_db(message):
    try:
        args = message.text.split(';')
        db.insert('category', {'codename': args[0], 'name': args[1], 'aliases': args[2]})
        bot.send_message(message.chat.id,
                         text='Категория успешно добавлена'
                              '\nСписок категорий: /categories ')

    except IntegrityError as ie:
        print(repr(ie))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("⬅", callback_data='c_back'))
        msg = bot.send_message(message.chat.id,
                               'Категория с данным codename уже существует. Codename должен быть уникальным. \nПример: codename;name;a1,a2,a3',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_category_to_db)

    except Exception as e:
        print(repr(e))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("⬅", callback_data='c_back'))
        msg = bot.send_message(message.chat.id, 'Неверный формат категории. \nПример: codename;name;a1,a2,a3',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_category_to_db)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'm_category':
                add_category_header(call.message)
            elif call.data == 'm_record':
                bot.send_message(call.message.chat.id, 'Запись добавлена(' + call.message.text + ')')
            elif call.data == 'm_back':
                helper(call.message)
            elif call.data == 'c_back':
                bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text='Спасибо что заглянул',
                                  reply_markup=None)
    except Exception as e:
        print('AAAA ERRORRR ' + repr(e))


@bot.message_handler(commands=['categories'])
def categories_list(message):
    categories = Categories().get_all_categories()
    answer_message = "Категории:\n\n* " + \
                     ("\n* ".join([c.name + ' (' + ", ".join(c.aliases) + ')' for c in categories]))
    bot.send_message(message.chat.id, answer_message)


@bot.message_handler(commands=['cases'])
def list_cases(message):
    last_records = records.last()
    if not last_records:
        bot.send_message(message.chat.id, 'Нет записей')
        return

    last_records_rows = [
        f"{record.time_count} учила {record.category_codename} — нажми "
        f"/del{record.id} для удаления"
        for record in last_records]
    answer_message = "Последние сохранённые записи:\n\n* " + "\n\n* " \
        .join(last_records_rows)
    bot.send_message(message.chat.id, answer_message)


@bot.message_handler(content_types=['text'])
def random_text(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton("Добавить категорию", callback_data='m_category')
    item2 = types.InlineKeyboardButton("Добавить запись", callback_data='m_record')
    item3 = types.InlineKeyboardButton("⬅", callback_data='m_back')
    markup.add(item3, item1, item2)
    bot.send_message(message.chat.id, 'Что-то хотели?', reply_markup=markup)


# @bot.message_handler(content_types=['text'])
# async def add_record(message: types.Message):
#   try:
#       record = records.add_record(message.text)
#  except exceptions.NotCorrectMessage as e:
#     bot.send_message(message.chat.id,str(e))
#     return
# answer_message = (
#    f"Добавлены траты {record.amount} руб на {record.category_name}.\n\n"
#    f"{records.get_today_statistics()}")
# bot.send_message(message.chat.id, answer_message)


# @bot.message_handler(content_types=['text'])
# def myAnswer(message):
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


# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
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
