from sqlite3 import IntegrityError

import telebot
from telebot import types
from random import randint
import resourses.database.database as db
from model.categories import Categories
from model.records import Records as records
from resourses import config
import components as cmp

bot = telebot.TeleBot(config.API_TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('resourses/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!\n Я - <b>СобакаБот</b>, созданный '
                                      'чтобы помочь вам отслеживать свое время в обучении! '
                     .format(message.from_user),
                     parse_mode='html')
    helper(message)


@bot.message_handler(commands=['help'])
def helper(message):
    bot.send_message(message.chat.id,
                     "Последние записи: /records\n"
                     "Добавить категорию: /add_category\n"
                     "Добавить запись: /add_time_record\n"
                     "Категории: /categories")


@bot.message_handler(commands=['categories'])
def categories_list(message):
    categories = Categories().get_all_categories()
    answer_message = "Категории:\n\n* " + \
                     ("\n* ".join([c.name + ' (' + ", ".join(c.aliases) + ')' for c in categories]))

    bot.send_message(message.chat.id, answer_message,
                     reply_markup=cmp.back_to_menu_inline_markup(), parse_mode='HTML')


@bot.message_handler(commands=['add_category'])
def add_category_header(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("⬅", callback_data='back_to_menu'))
    msg = bot.send_message(message.chat.id,
                           'Введите кодовое название, полное название и псевдонимы категории через ; ',
                           reply_markup=markup)
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
                               'Категория с данным codename уже существует. Codename должен быть уникальным. '
                               '\nПример: codename;name;a1,a2,a3',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_category_to_db)

    except Exception as e:
        print(repr(e))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("⬅", callback_data='c_back'))
        msg = bot.send_message(message.chat.id, 'Неверный формат категории. \nПример: codename;name;a1,a2,a3',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_category_to_db)


@bot.message_handler(commands=['add_time_record'])
def add_time_record_header(message):
    msg = bot.send_message(message.chat.id,
                           'Введите время и категорию через ; ',
                           reply_markup=cmp.back_to_menu_inline_markup(), parse_mode='HTML')
    bot.register_next_step_handler(msg, add_time_record_to_db)


def add_time_record_to_db(message):
    try:
        args = message.text.split(';')
        db.insert('record', {'id': None,
                             # 'created': datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d
                             # %H:%M:%S"),
                             'time_count': args[0], 'category_codename': args[1], 'raw_text': message.text})
        bot.send_message(message.chat.id,
                         text='Запись успешно добавлена'
                              '\nСписок записей: /records ')

    except Exception as e:
        print(repr(e))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("⬅", callback_data='c_back'))
        msg = bot.send_message(message.chat.id, 'Неверный формат записи. \nПример: 10 минут ; чтение',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_time_record_to_db)


@bot.message_handler(commands=['records'])
def records_list(message):
    answer_message = "Записи:\n\n* " + \
                     ("\n* ".join([r.time_count + "  " + r.category_codename for r in records.load_records()]))
    bot.send_message(message.chat.id, answer_message, reply_markup=cmp.back_to_menu_inline_markup(), parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'm_category':
                add_category_header(call.message)
            elif call.data == 'm_record':
                add_time_record_header(call.message)
            elif call.data == 'back_to_menu':
                helper(call.message)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text=call.message.text,
                                  reply_markup=None)
            if call.data == 'c_back':
                bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id, text=call.message.text,
                                      reply_markup=cmp.back_to_menu_inline_markup(), parse_mode='HTML')
    except Exception as e:
        print(repr(e))


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
    sti = open('resourses/stickers/' + str(randint(1, 54)) + '.webp', 'rb')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('/start')
    markup.add(button)
    bot.send_sticker(message.chat.id, sti, reply_markup=markup)


bot.polling(none_stop=True)
