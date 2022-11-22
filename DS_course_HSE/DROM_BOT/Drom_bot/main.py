import telebot
from telebot import types

from secret import token

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import numpy as np
import pandas as pd
import pymorphy2
import re
import os
import dataframe_image as dfi
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker
import hashlib

from get_posters import get_posters

bot = telebot.TeleBot(token)

user_dict = dict()

try:
    query_hash_dict = np.load(
        'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\dictionaries\\query_hash_dict.npy',
        allow_pickle=True).item()
except:
    query_hash_dict = dict()


class User:
    def __init__(self, name):
        self.name = name
        self.home_region = None
        self.home_region_num = None
        self.home_region_lit = None
        self.search_region = None
        self.search_region_num = None
        self.search_region_lit = None
        self.search_city_eng = None
        self.search_city_rus = None
        self.search_city_lit = None
        self.brand_choice = None
        self.brand_choice_lit = None
        self.model_choice = None
        self.model_choice_lit = None
        self.query = None
        self.query_status = 0
        self.query_count = None
        self.last_queries = []
        self.limit = None


regions_cities_dict = np.load(
    'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\basic_dictionaries\\regions_cities_dict.npy',
    allow_pickle=True).item()
brands_models_dict = np.load('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\basic_dictionaries\\brands_models_dict.npy',
                             allow_pickle=True).item()

chrome_options = Options()
chrome_options.add_argument("--headless")
s = Service('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\driver\\geckodriver.exe')
driver = webdriver.Firefox(options=chrome_options, service=s)


@bot.message_handler(func=lambda message: message.text.strip().lower() == '/start')  # commands=['start']
def send_welcome(message):
    global user_dict
    welcome_text = f'''
    Привет, <b>{message.from_user.first_name}!</b>.
    
    Вы успешно авторизировались ✅
    
    Для того, чтобы посмотреть доступные команды, нажмите /help.

    Обо мне можно прочитать здесь - /info.
    '''
    bot.send_message(message.chat.id, welcome_text, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())

    chat_id = message.chat.id

    try:
        user_dict = np.load(
            f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\dictionaries\\user_dict.npy',
            allow_pickle=True).item()
        user = user_dict.get(chat_id)
        bot.send_message(message.chat.id,
                         f'''
        <b>Мы c Вами уже знакомы и я помню Ваш прошлый запрос:</b>                                                 
        \n---------------------------------------
        \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
        \n---------------------------------------
        ''', parse_mode='html')

        bot.send_message(message.chat.id, '''
Если Вы хотите перезаписать текущий запрос, введите /dialog.
Либо Вы можете найти объявления по текущему запросу - /posters.
            ''')

    except:
        bot.send_message(message.chat.id, '''
<b>Мы c Вами еще не знакомы.
Давайте составим запрос:</b> /dialog.''',
                         parse_mode='html')
        name = message.from_user.first_name
        user = User(name)
        user_dict[chat_id] = user

    keyboard = types.InlineKeyboardMarkup()
    url_button_location = types.InlineKeyboardButton(text="Регионов и населенных пунктов",
                                                     url="https://auto.drom.ru/cities/")
    url_button_cars = types.InlineKeyboardButton(text="Марок и моделей", url="https://www.drom.ru/catalog/")
    keyboard.add(url_button_location)
    keyboard.add(url_button_cars)
    bot.send_message(message.chat.id,
                     'Перед началом работы (особенно в первый раз) крайне рекомендую ознакомиться с правилами ввода информации - /info.')
    bot.send_message(message.chat.id, "Здесь также можно посмотреть все возможные варинаты для ввода:",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text.strip().lower() == '/rules')  # commands=['rules']
def send_rules(message):
    text = '''
<b> ❗ Правила ввода названия регионов и населенных пунктов:</b>
    
    1) Названия регионов и населенных пунктов вводятся только на русском языке.
    2) Регионы вводятся со словами область / край / республика / автономный округ / автономная область 
    (кроме Москвы и Санкт-Петербурга), через пробел, регистр не важен. 
    3) В названиях населенных пунктов также проставляются дефисы и цифры (при наличии), через пробел, регистр не важен.
    4) При необходимости ввести населенный пункт в регионах Москва и Санкт-Петербург, вводятся города Москва и Санкт-Петербург, соответственно.

<b> ❗ Правила ввода названия марок и моделей:</b>
    
    1) Названия марок и моделей вводятся на русском и английском языках.
    2) В названиях марок и моделей проставляются пробелы, дефисы (при наличии), регистр не важен.
    '''
    bot.send_message(message.chat.id, text, parse_mode='html')


@bot.message_handler(func=lambda message: message.text.strip().lower() == '/help')  # commands=['help']
def send_help(message):
    bot.send_message(message.chat.id,
                     '''
<b>Список доступных Вам команд:</b>

    /start - запуск бота, авторизация

    /rules - правила ввода информации

    /help - список доступных команд

    /info - описание функциональности бота

    /dialog - формирование запроса

    /posters - выдача объявлений по запросу
''', parse_mode='html')


@bot.message_handler(func=lambda message: message.text.strip().lower() == '/info')  # commands=['info']
def send_info(message):
    bot.send_message(message.chat.id,
                     '''
    <b>Drom_bot</b> - это бот, который умеет:
    ✅ делать запросы и собирать информацию с сайта Drom.ru
    ✅ показывать объявления (и историю изменения цены на конкретное авто)
    ✅ показывать сводную информацию по Вашему запросу
    
Для того, чтобы начать работу,
необходимо авторизироваться: /start.
Затем появится возможность сформировать запрос: /dialog. 
И только после этого вы сможете
запросить объявления /posters.
Именно в таком порядке и никак иначе 👀

Авторизировавшись и сформировав запрос, бот запоминает
информацию. В будущем вы можете снова вывести объявления
по последнему зафиксированному запросу или же перезаписать, посмотрев новые предложения.

Вы также можете в любой момент:
перезапустить бота, авторизировавшись заново - /start 
запросить список досутпных команд - /help
запросить описание функциональности бота - /info
''', parse_mode='html')


@bot.message_handler(func=lambda message: message.text.strip().lower() not in (
        '/start', '/rules', '/help', '/info', '/dialog', '/posters'))
def unknown_message(message):
    bot.send_message(message.chat.id,
                     'Извините, я Вас не понимаю. Пожалуйста, используйте соответствующие команды: /help.')


@bot.message_handler(
    content_types=['photo', 'sticker', 'pinned_message', 'audio', 'document', 'video', 'voice', 'video_note',
                   'location', 'contact'])
def unknown_media(message):
    bot.send_message(message.chat.id,
                     text='Извините, я Вас не понимаю. Пожалуйста, используйте соответствующие команды: /help.')


@bot.message_handler(func=lambda message: message.text.strip().lower() == '/dialog')  # commands=["dialog"]
def dialog(message):
    global user_dict
    chat_id = message.chat.id
    if user_dict.get(chat_id) is None:
        bot.send_message(message.chat.id, 'Вы еще не авторизировались. Введите /start, чтобы авторизироваться.')
    elif user_dict.get(chat_id).query_status == 1:
        msg = bot.send_message(message.chat.id,
                               'Вы уже ранее составили запрос, но мы без проблем его перезапишем. Пожалуйста, введите Ваш домашний регион')

        user = user_dict[chat_id]
        saved_query_count = user.query_count
        saved_last_queries = user.last_queries

        name = message.from_user.first_name
        user = User(name)
        user.query_count = saved_query_count
        user.last_queries = saved_last_queries

        user_dict[chat_id] = user
        bot.register_next_step_handler(msg, home_region_choice_step)
    else:
        msg = bot.send_message(message.chat.id,
                               'Давайте составим Ваш первый запрос. Пожалуйста, введите Ваш домашний регион')
        bot.register_next_step_handler(msg, home_region_choice_step)


user_padezh_region = str()


def home_region_choice_step(message):
    global user_padezh_region
    user_home_region = message.text.lower().strip()

    if user_home_region == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif user_home_region == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите Ваш домашний регион')
        bot.register_next_step_handler(msg, home_region_choice_step)
    elif user_home_region == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите Ваш домашний регион')
        bot.register_next_step_handler(msg, home_region_choice_step)
    elif regions_cities_dict.get(user_home_region) is None:
        msg = bot.reply_to(message, 'Вы неверно ввели регион, попробуйте еще раз: впишите название региона корректно.')
        bot.register_next_step_handler(msg, home_region_choice_step)
    else:
        bot.reply_to(message, 'Проверяю Ваш регион в имеющемся у меня списке.')

        morph = pymorphy2.MorphAnalyzer()

        try:
            if user_home_region.split(' ')[-1] == 'край':
                user_padezh_region = user_home_region[0].upper() + user_home_region[1:]
            elif user_home_region.split(' ')[-1] == 'область':
                if user_home_region.split(' ')[0] == 'еврейская':
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    morph.parse(user_home_region.split(' ')[1])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[2]
                    user_padezh_region = padezh_region[0].upper() + padezh_region[1:]
                else:
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[1]
                    user_padezh_region = padezh_region[0].upper() + padezh_region[1:]
            elif user_home_region.split(' ')[-1] == 'округ':
                if user_home_region.split(' ')[0] == 'ханты-мансийский' or user_home_region.split(' ')[
                    0] == 'ямало-ненецкий':
                    user_padezh_region = user_home_region.split('-')[0][0].upper() + user_home_region.split('-')[0][
                                                                                     1:] + '-' + \
                                         user_home_region.split('-')[1][0].upper() + \
                                         user_home_region.split('-')[1][1:]
                else:
                    user_padezh_region = user_home_region[0].upper() + user_home_region[1:]
            elif user_home_region.split(' ')[0] == 'республика':
                if len(user_home_region.split(' ')) == 2:
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[1]
                    user_padezh_region = padezh_region.title()
                else:
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[1] + ' ' + user_home_region.split(' ')[2]
                    user_padezh_region = padezh_region.title()
            else:
                padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                morph.parse(user_home_region.split(' ')[1])[
                                    0].inflect({'accs'}).word
                user_padezh_region = padezh_region.title()
        except:
            user_padezh_region = morph.parse(user_home_region)[0].inflect({'accs'}).word.title()

        bot.send_message(message.chat.id, 'Отлично, я поставил {} в качестве домашнего региона. '
                                          'Это позволит правильно определить размер налога на авто в Вашем регионе.'
                         .format(user_padezh_region))

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.home_region = user_home_region
        user.home_region_num = regions_cities_dict.get(user_home_region)[0]
        user.home_region_lit = regions_cities_dict.get(user_home_region)[1]

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По целому региону', 'По населенному пункту')

        msg = bot.send_message(message.chat.id, 'Какой вид поиска будете осуществлять?', reply_markup=markup)
        bot.register_next_step_handler(msg, locality_choice_step)


def locality_choice_step(message):
    locality_choice = message.text
    if locality_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь', reply_markup=types.ReplyKeyboardRemove())
        send_welcome(message)
    elif locality_choice == '/help':
        bot.send_message(message.chat.id, 'Прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_help(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По целому региону', 'По населенному пункту')
        msg = bot.send_message(message.chat.id, 'Какой вид поиска будете осуществлять?', reply_markup=markup)
        bot.register_next_step_handler(msg, locality_choice_step)
    elif locality_choice == '/info':
        bot.send_message(message.chat.id, 'Прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_info(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По целому региону', 'По населенному пункту')
        msg = bot.send_message(message.chat.id, 'Какой вид поиска будете осуществлять?', reply_markup=markup)
        bot.register_next_step_handler(msg, locality_choice_step)

    elif locality_choice == 'По целому региону':
        bot.reply_to(message, 'Вы выбрали поиск по целому региону', reply_markup=types.ReplyKeyboardRemove())
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По моему домашненму региону', 'Выберем другой')
        msg = bot.send_message(message.chat.id, 'Будем искать по Вашему домашнему региону или выберем другой?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, region_search_choice_step)
    elif locality_choice == 'По населенному пункту':
        bot.reply_to(message, 'Вы выбрали поиск по определенному населенному пункту',
                     reply_markup=types.ReplyKeyboardRemove())
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В моем домашнем регионе', 'Выберем другой')
        msg = bot.send_message(message.chat.id,
                               'Населенный пункт находится в Вашем домашнем регионе или выберем другой?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, city_search_choice_step)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По целому региону', "По определенному населенному пункту")
        msg = bot.send_message(message.chat.id, 'Вы не выбрали, какой вид поиска будете осуществлять.',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, locality_choice_step)


def region_search_choice_step(message):
    region_choice = message.text
    if region_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь', reply_markup=types.ReplyKeyboardRemove())
        send_welcome(message)

    elif region_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_help(message)
        bot.send_message(message.chat.id, 'Вы выбрали поиск по целому региону')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По моему домашненму региону', 'Выберем другой')
        msg = bot.send_message(message.chat.id, 'Будем искать по Вашему домашнему региону или выберем другой?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, region_search_choice_step)
    elif region_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_info(message)
        bot.send_message(message.chat.id, 'Вы выбрали поиск по целому региону')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По моему домашненму региону', 'Выберем другой')
        msg = bot.send_message(message.chat.id, 'Будем искать по Вашему домашнему региону или выберем другой?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, region_search_choice_step)

    elif region_choice == 'По моему домашненму региону':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.search_region = user.home_region
        user.search_region_num = user.home_region_num
        user.search_region_lit = user.home_region_lit
        query = 'auto.drom.ru/region{}/'.format(user.search_region_num)
        user.query = query
        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск авто по Вашему домашнему региону',
                         reply_markup=types.ReplyKeyboardRemove())

        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти')
        bot.register_next_step_handler(msg, brand_choice_step)

    elif region_choice == 'Выберем другой':
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, region_search_choice_step_2)

    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('По моему домашненму региону', 'Выберем другой')
        msg = bot.send_message(message.chat.id, 'Вы не выбрали, какой вид поиска будете осуществять.',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, region_search_choice_step)


def region_search_choice_step_2(message):
    user_search_region = message.text.lower().strip()

    if user_search_region == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif user_search_region == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, region_search_choice_step_2)
    elif user_search_region == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, region_search_choice_step_2)

    elif regions_cities_dict.get(user_search_region) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели регион, попробуйте еще раз: впишите название региона корректно.')
        bot.register_next_step_handler(msg, region_search_choice_step_2)

    else:
        bot.reply_to(message, 'Проверяю данный регион в имеющемся у меня списке.')

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.search_region = user_search_region
        user.search_region_num = regions_cities_dict.get(user_search_region)[0]
        user.search_region_lit = regions_cities_dict.get(user_search_region)[1]
        query = 'auto.drom.ru/region{}/'.format(user.search_region_num)
        user.query = query
        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск по данному региону')

        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти')
        bot.register_next_step_handler(msg, brand_choice_step)


def city_search_choice_step(message):
    city_choice = message.text

    if city_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь', reply_markup=types.ReplyKeyboardRemove())
        send_welcome(message)

    elif city_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_help(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В моем домашнем регионе', 'Выберем другой')
        msg = bot.send_message(message.chat.id,
                               'Населенный пункт находится в Вашем домашнем регионе или выберем другой?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, city_search_choice_step)
    elif city_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_info(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В моем домашнем регионе', 'Выберем другой')
        msg = bot.send_message(message.chat.id,
                               'Населенный пункт находится в Вашем домашнем регионе или выберем другой?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, city_search_choice_step)

    elif city_choice == 'В моем домашнем регионе':

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.search_region = user.home_region
        user.search_region_num = user.home_region_num
        user.search_region_lit = user.home_region_lit

        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, city_search_choice_step_3)

    elif city_choice == 'Выберем другой':
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, city_search_choice_step_2)

    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В моем домашнем регионе', 'Выберем другой')
        msg = bot.send_message(message.chat.id, 'Вы не выбрали, какой вид поиска будете осуществять.',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, city_search_choice_step)


def city_search_choice_step_2(message):
    user_search_region = message.text.lower().strip()

    if user_search_region == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif user_search_region == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, city_search_choice_step_2)
    elif user_search_region == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, city_search_choice_step_2)

    elif regions_cities_dict.get(user_search_region) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели регион, попробуйте еще раз: впишите название региона корректно.')
        bot.register_next_step_handler(msg, city_search_choice_step_2)

    else:
        bot.reply_to(message, 'Проверяю данный регион в имеющемся у меня списке.')

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.search_region = user_search_region
        user.search_region_num = regions_cities_dict.get(user_search_region)[0]
        user.search_region_lit = regions_cities_dict.get(user_search_region)[1]

        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск по данному региону')

        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, city_search_choice_step_3)


def city_search_choice_step_3(message):
    user_search_city_rus = message.text.lower().strip()
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if user_search_city_rus == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif user_search_city_rus == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, city_search_choice_step_3)

    elif user_search_city_rus == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, city_search_choice_step_3)

    elif regions_cities_dict.get(user.search_region)[2].get(user_search_city_rus) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели название населенного пункта, попробуйте еще раз: впишите название населенного пункта корректно.')
        bot.register_next_step_handler(msg, city_search_choice_step_3)
        return
    else:
        search_city_eng = regions_cities_dict.get(user.search_region)[2].get(user_search_city_rus)[0]
        user.search_city_eng = search_city_eng
        user.search_city_rus = user_search_city_rus
        user.search_city_lit = regions_cities_dict.get(user.search_region)[2].get(user_search_city_rus)[1]

        query = '{}.drom.ru/'.format(user.search_city_eng)
        user.query = query
        bot.send_message(message.chat.id,
                         'Хорошо, осуществим поиск авто в данном населенном пунтке')

        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти')
        bot.register_next_step_handler(msg, brand_choice_step)


def brand_choice_step(message):
    brand_choice = message.text.lower().strip()

    if brand_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif brand_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти')
        bot.register_next_step_handler(msg, brand_choice_step)

    elif brand_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти')
        bot.register_next_step_handler(msg, brand_choice_step)

    elif brands_models_dict.get(brand_choice) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели название марки авто, попробуйте еще раз: впишите название марки авто корректно.')
        bot.register_next_step_handler(msg, brand_choice_step)
        return
    else:
        bot.reply_to(message, 'Проверяю данную марку авто в имеющемся у меня списке.')

        chat_id = message.chat.id
        user = user_dict[chat_id]

        user.brand_choice = brands_models_dict.get(brand_choice)[0]
        user.brand_choice_lit = brands_models_dict.get(brand_choice)[1]

        user.query = user.query + user.brand_choice + '/'
        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск по данной марке')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Только по марке', 'По марке и модели')
        msg = bot.send_message(message.chat.id, 'Какой вид поиска будете осуществлять?', reply_markup=markup)
        bot.register_next_step_handler(msg, model_choice_step)


def model_choice_step(message):
    model_search = message.text
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if model_search == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь', reply_markup=types.ReplyKeyboardRemove())
        send_welcome(message)

    elif model_search == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_help(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Только по марке', 'По марке и модели')
        msg = bot.send_message(message.chat.id, 'Какой вид поиска будете осуществлять?', reply_markup=markup)
        bot.register_next_step_handler(msg, model_choice_step)

    elif model_search == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_info(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Только по марке', 'По марке и модели')
        msg = bot.send_message(message.chat.id, 'Какой вид поиска будете осуществлять?', reply_markup=markup)
        bot.register_next_step_handler(msg, model_choice_step)

    elif model_search == 'Только по марке':

        bot.send_message(message.chat.id,
                         'Хорошо, осуществим поиск только по марке',
                         reply_markup=types.ReplyKeyboardRemove())

        bot.send_message(message.chat.id,
                         f'''
                         <b>Введенные данные:</b>
                         \n---------------------------------------
                         \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                         ''',
                         parse_mode='html')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)

    elif model_search == 'По марке и модели':
        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск по марке и модели',
                         reply_markup=types.ReplyKeyboardRemove())
        msg = bot.send_message(message.chat.id, 'Введите название модели авто, которое хотите найти')
        bot.register_next_step_handler(msg, model_choice_step_2)

    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Только по марке', 'По марке и модели')

        msg = bot.send_message(message.chat.id, 'Вы не выбрали, какой вид поиска будете осуществлять?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, model_choice_step)


def model_choice_step_2(message):
    model_choice = message.text.lower().strip()

    chat_id = message.chat.id
    user = user_dict[chat_id]

    if model_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif model_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Введите название модели авто, которое хотите найти')
        bot.register_next_step_handler(msg, model_choice_step_2)

    elif model_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Введите название модели авто, которое хотите найти')
        bot.register_next_step_handler(msg, model_choice_step_2)

    elif brands_models_dict.get(user.brand_choice)[2].get(model_choice) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели название модели, попробуйте еще раз: впишите название модели корректно.')
        bot.register_next_step_handler(msg, model_choice_step_2)
        return
    else:
        bot.reply_to(message, 'Проверяю данную модель авто в имеющемся у меня списке.')

        user.model_choice = brands_models_dict.get(user.brand_choice)[2].get(model_choice)[0]
        user.model_choice_lit = brands_models_dict.get(user.brand_choice)[2].get(model_choice)[1]

        user.query = user.query + user.model_choice + '/'
        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск по данной модели')

        bot.send_message(message.chat.id,
                         f'''
                         <b>Введенные данные:</b>
                         \n---------------------------------------
                         \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                         ''',
                         parse_mode='html')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)


def make_query_step(message):
    chat_id = message.chat.id

    user = user_dict[chat_id]

    query_choice = message.text

    if query_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь', reply_markup=types.ReplyKeyboardRemove())
        send_welcome(message)

    elif query_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_help(message)

        bot.send_message(message.chat.id,
                         f'''
                         <b>Введенные данные:</b>
                         \n---------------------------------------
                         \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                         ''',
                         parse_mode='html')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)

    elif query_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_info(message)

        bot.send_message(message.chat.id,
                         f'''
                         <b>Введенные данные:</b>
                         \n---------------------------------------
                         \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                         ''',
                         parse_mode='html')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)

    elif query_choice == 'Да':
        bot.send_message(message.chat.id, 'Отлично, мы закончили с формированием запроса.'.format(user.query),
                         reply_markup=types.ReplyKeyboardRemove())
        user.query = 'https://' + user.query
        user.query_status = 1

        user.query_count = user.last_queries.count(user.query)

        np.save(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\dictionaries\\user_dict.npy',
                user_dict)
        bot.send_message(message.chat.id, 'Введите /posters, чтобы продолжить и найти объявления'.format(user.query))

    elif query_choice == 'Нет':
        bot.send_message(message.chat.id, 'Ничего страшного', reply_markup=types.ReplyKeyboardRemove())

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В домашнем регионе', 'В регионе поиска', 'В населенном пункте', 'В марке', 'В модели')

        msg = bot.send_message(message.chat.id, 'Где находится ошибка?', reply_markup=markup)
        bot.register_next_step_handler(msg, remarks_step)

    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Вы не подтвердили правильность данных. Все введенные данные верны?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)


def remarks_step(message):
    bot.send_message(message.chat.id, 'Давайте устраним ошибку!', reply_markup=types.ReplyKeyboardRemove())
    remark_choice = message.text

    if remark_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь', reply_markup=types.ReplyKeyboardRemove())
        send_welcome(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В домашнем регионе', 'В регионе поиска', 'В населенном пункте', 'В марке', 'В модели')
        msg = bot.send_message(message.chat.id, 'Где находится ошибка?', reply_markup=markup)
        bot.register_next_step_handler(msg, remarks_step)

    elif remark_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_help(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В домашнем регионе', 'В регионе поиска', 'В населенном пункте', 'В марке', 'В модели')
        msg = bot.send_message(message.chat.id, 'Где находится ошибка?', reply_markup=markup)
        bot.register_next_step_handler(msg, remarks_step)

    elif remark_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_info(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В домашнем регионе', 'В регионе поиска', 'В населенном пункте', 'В марке', 'В модели')
        msg = bot.send_message(message.chat.id, 'Где находится ошибка?', reply_markup=markup)
        bot.register_next_step_handler(msg, remarks_step)

    elif remark_choice == 'В домашнем регионе':
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите Ваш домашний регион',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, home_region_choice_step_remark)

    elif remark_choice == 'В регионе поиска':
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, region_search_choice_step_remark)

    elif remark_choice == 'В населенном пункте':
        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.'
                               ' Он должен обязательно находиться в регионе поиска, который вы указали ранее.',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, city_search_choice_step_remark)

    elif remark_choice == 'В марке':
        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, brand_choice_step_remark)

    elif remark_choice == 'В модели':
        msg = bot.send_message(message.chat.id,
                               'Введите название модели авто, которое хотите найти. Обратите внимание, моедль должна принадлежать выбранной ранее марке!',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, model_choice_step_remark)

    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('В домашнем регионе', 'В регионе поиска', 'В населенном пункте', 'В марке', 'В модели')

        msg = bot.send_message(message.chat.id, 'Вы не выбрали, где находится ошибка?', reply_markup=markup)
        bot.register_next_step_handler(msg, remarks_step)


def home_region_choice_step_remark(message):
    user_home_region = message.text.lower().strip()
    global user_padezh_region

    if user_home_region == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif user_home_region == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите Ваш домашний регион')
        bot.register_next_step_handler(msg, home_region_choice_step_remark)

    elif user_home_region == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите Ваш домашний регион')
        bot.register_next_step_handler(msg, home_region_choice_step_remark)

    elif regions_cities_dict.get(user_home_region) is None:
        msg = bot.reply_to(message, 'Вы неверно ввели регион, попробуйте еще раз: впишите название региона корректно.')
        bot.register_next_step_handler(msg, home_region_choice_step_remark)
        return
    else:
        bot.reply_to(message, 'Проверяю Ваш регион в имеющемся у меня списке.')

        morph = pymorphy2.MorphAnalyzer()

        try:
            if user_home_region.split(' ')[-1] == 'край':
                user_padezh_region = user_home_region[0].upper() + user_home_region[1:]
            elif user_home_region.split(' ')[-1] == 'область':
                if user_home_region.split(' ')[0] == 'еврейская':
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    morph.parse(user_home_region.split(' ')[1])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[2]
                    user_padezh_region = padezh_region[0].upper() + padezh_region[1:]
                else:
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[1]
                    user_padezh_region = padezh_region[0].upper() + padezh_region[1:]
            elif user_home_region.split(' ')[-1] == 'округ':
                if user_home_region.split(' ')[0] == 'ханты-мансийский' or user_home_region.split(' ')[
                    0] == 'ямало-ненецкий':
                    user_padezh_region = user_home_region.split('-')[0][0].upper() + user_home_region.split('-')[0][
                                                                                     1:] + '-' + \
                                         user_home_region.split('-')[1][0].upper() + \
                                         user_home_region.split('-')[1][1:]
                else:
                    user_padezh_region = user_home_region[0].upper() + user_home_region[1:]
            elif user_home_region.split(' ')[0] == 'республика':
                if len(user_home_region.split(' ')) == 2:
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[1]
                    user_padezh_region = padezh_region.title()
                else:
                    padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                    user_home_region.split(' ')[1] + ' ' + user_home_region.split(' ')[2]
                    user_padezh_region = padezh_region.title()
            else:
                padezh_region = morph.parse(user_home_region.split(' ')[0])[0].inflect({'accs'}).word + ' ' + \
                                morph.parse(user_home_region.split(' ')[1])[
                                    0].inflect({'accs'}).word
                user_padezh_region = padezh_region.title()
        except:
            user_padezh_region = morph.parse(user_home_region)[0].inflect({'accs'}).word.title()

        bot.send_message(message.chat.id, 'Отлично, я поставил {} в качестве домашнего региона. '
                                          'Это позволит правильно определить размер налога на авто в Вашем регионе.'
                         .format(user_padezh_region))

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.home_region = user_home_region
        user.home_region_num = regions_cities_dict.get(user_home_region)[0]
        user.home_region_lit = regions_cities_dict.get(user_home_region)[1]

        bot.send_message(message.chat.id,
                         f'''
                         <b>Введенные данные:</b>
                         \n---------------------------------------
                         \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                         ''', parse_mode='html')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)


def region_search_choice_step_remark(message):
    user_search_region = message.text.lower().strip()
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if user_search_region == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif user_search_region == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, region_search_choice_step_remark)

    elif user_search_region == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите название региона, в котором хотите найти авто.')
        bot.register_next_step_handler(msg, region_search_choice_step_remark)

    elif regions_cities_dict.get(user_search_region) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели регион, попробуйте еще раз: впишите название региона корректно.')
        bot.register_next_step_handler(msg, region_search_choice_step_remark)
        return
    else:
        bot.reply_to(message, 'Проверяю данный регион в имеющемся у меня списке.')
        user.search_region = user_search_region
        user.search_region_num = regions_cities_dict.get(user_search_region)[0]
        user.search_region_lit = regions_cities_dict.get(user_search_region)[1]

        if user.model_choice is None:
            query = 'auto.drom.ru/region{}/{}/'.format(user.search_region_num, user.brand_choice)
        else:
            query = 'auto.drom.ru/region{}/{}/{}/'.format(user.search_region_num, user.brand_choice, user.model_choice)
        user.query = query
        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск по данному региону.')

    if user.search_city_rus is not None:

        bot.send_message(message.chat.id, 'Вы изменили регион поиска, '
                                          'поэтому сейчас необходимо выбрать новый населенный пункт для поиска.')

        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, city_search_choice_step_remark)

    else:
        bot.send_message(message.chat.id,
                         f'''
                         <b>Введенные данные:</b>
                         \n---------------------------------------
                         \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                         ''',
                         parse_mode='html')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)


def city_search_choice_step_remark(message):
    user_search_city_rus = message.text.lower().strip()
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if user_search_city_rus == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif user_search_city_rus == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.'
                               ' Он должен обязательно находиться в регионе поиска, который вы указали ранее.')
        bot.register_next_step_handler(msg, city_search_choice_step_remark)

    elif user_search_city_rus == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id,
                               'Пожалуйста, введите название населенного пункта, в котором хотите найти авто.'
                               ' Он должен обязательно находиться в регионе поиска, который вы указали ранее.')
        bot.register_next_step_handler(msg, city_search_choice_step_remark)

    elif regions_cities_dict.get(user.search_region)[2].get(user_search_city_rus) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели название населенного пункта, попробуйте еще раз: впишите название населенного пункта корректно.'
                           ' Возможно, Вы ввели название населенного пункта, которого нет в указанном регионе поиска.')
        bot.register_next_step_handler(msg, city_search_choice_step_remark)
        return
    else:
        search_city_eng = regions_cities_dict.get(user.search_region)[2].get(user_search_city_rus)[0]
        user.search_city_eng = search_city_eng
        user.search_city_rus = user_search_city_rus
        user.search_city_lit = regions_cities_dict.get(user.search_region)[2].get(user_search_city_rus)[1]

        if user.model_choice is None:
            query = '{}.drom.ru/{}/'.format(user.search_city_eng, user.brand_choice)
        else:
            query = '{}.drom.ru/{}/{}/'.format(user.search_city_eng, user.brand_choice, user.model_choice)

        user.query = query
        bot.send_message(message.chat.id,
                         'Хорошо, осуществим поиск авто в данном населенном пунтке')

        bot.send_message(message.chat.id,
                         f'''
                         <b>Введенные данные:</b>
                         \n---------------------------------------
                         \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                         ''',
                         parse_mode='html')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
        bot.register_next_step_handler(msg, make_query_step)


def brand_choice_step_remark(message):
    brand_choice = message.text.lower().strip()

    if brand_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif brand_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти')
        bot.register_next_step_handler(msg, brand_choice_step_remark)

    elif brand_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id, 'Введите название марки авто, которое хотите найти')
        bot.register_next_step_handler(msg, brand_choice_step_remark)

    elif brands_models_dict.get(brand_choice) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели название марки авто, попробуйте еще раз: впишите название марки авто корректно.')
        bot.register_next_step_handler(msg, brand_choice_step_remark)
        return
    else:
        bot.reply_to(message, 'Проверяю данную марку авто в имеющемся у меня списке.')

        chat_id = message.chat.id
        user = user_dict[chat_id]

        user.brand_choice = brands_models_dict.get(brand_choice)[0]
        user.brand_choice_lit = brands_models_dict.get(brand_choice)[1]

        if user.search_city_eng is None:
            query = 'auto.drom.ru/region{}/{}/'.format(user.search_region_num, user.brand_choice)
        else:
            query = '{}.drom.ru/{}/'.format(user.search_city_eng, user.brand_choice)

        user.query = query

        if user.model_choice is None:

            bot.send_message(message.chat.id,
                             f'''
                             <b>Введенные данные:</b>
                             \n---------------------------------------
                             \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                             ''',
                             parse_mode='html')

            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Да', 'Нет')
            msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
            bot.register_next_step_handler(msg, make_query_step)

        else:

            bot.send_message(message.chat.id, 'Вы изменили марку авто для поиска, '
                                              'поэтому сейчас необходимо выбрать новую модель.')

            msg = bot.send_message(message.chat.id, 'Введите название модели авто, которое хотите найти')
            bot.register_next_step_handler(msg, model_choice_step_remark)


def model_choice_step_remark(message):
    model_choice = message.text.lower().strip()

    chat_id = message.chat.id
    user = user_dict[chat_id]

    if model_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь')
        send_welcome(message)

    elif model_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_help(message)
        msg = bot.send_message(message.chat.id,
                               'Введите название модели авто, которое хотите найти. Обратите внимание, моедль должна принадлежать выбранному ранее бренду!')
        bot.register_next_step_handler(msg, model_choice_step_remark)

    elif model_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго')
        send_info(message)
        msg = bot.send_message(message.chat.id,
                               'Введите название модели авто, которое хотите найти. Обратите внимание, моедль должна принадлежать выбранному ранее бренду!')
        bot.register_next_step_handler(msg, model_choice_step_remark)

    elif brands_models_dict.get(user.brand_choice)[2].get(model_choice) is None:
        msg = bot.reply_to(message,
                           'Вы неверно ввели название модели, попробуйте еще раз: впишите название модели корректно.')
        bot.register_next_step_handler(msg, model_choice_step_remark)
        return
    else:
        bot.reply_to(message, 'Проверяю данную модель авто в имеющемся у меня списке.')

        user.model_choice = brands_models_dict.get(user.brand_choice)[2].get(model_choice)[0]
        user.model_choice_lit = brands_models_dict.get(user.brand_choice)[2].get(model_choice)[1]

        bot.send_message(message.chat.id, 'Хорошо, осуществим поиск по данной модели')

        if user.search_city_eng is None:
            query = 'auto.drom.ru/region{}/{}/{}/'.format(user.search_region_num, user.brand_choice, user.model_choice)
        else:
            query = '{}.drom.ru/{}/{}/'.format(user.search_city_eng, user.brand_choice, user.model_choice)

        user.query = query

    bot.send_message(message.chat.id,
                     f'''
                     <b>Введенные данные:</b>
                     \n---------------------------------------
                     \n<b>Домашний регион:</b> {user.home_region_lit}. \n<b>Регион поиска:</b> {user.search_region_lit}. \n<b>Населенный пункт для поиска:</b> {'Отсутствует' if user.search_city_rus is None else user.search_city_lit}.\n<b>Марка:</b> {user.brand_choice_lit}. \n<b>Модель:</b> {'Отсутствует' if user.model_choice is None else user.model_choice_lit}.
                     ''', parse_mode='html')

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Да', 'Нет')
    msg = bot.send_message(message.chat.id, 'Все введенные данные верны?', reply_markup=markup)
    bot.register_next_step_handler(msg, make_query_step)


@bot.message_handler(func=lambda message: message.text.strip().lower() == '/posters')  # commands=["posters"]
def posters_step(message):
    chat_id = message.chat.id

    if user_dict.get(chat_id) is None:
        bot.send_message(message.chat.id, 'Вы еще не авторизировались. Введите /start, чтобы авторизироваться.')
    else:
        user = user_dict[chat_id]
        if user.query_status == 1:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
                       '18', '19', '20')
            msg = bot.send_message(message.chat.id, 'Сколько объявлений вы хотите посмотреть?', reply_markup=markup)
            bot.register_next_step_handler(msg, posters_step_2)
        else:
            bot.send_message(message.chat.id,
                             'Вы еще не сформировали запрос. Введите /dialog, чтобы сформировать запрос.')


def posters_step_2(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    limit_choice = message.text.lower().strip()

    if limit_choice == '/start':
        bot.send_message(message.chat.id, 'Хорошо, перезапускаюсь', reply_markup=types.ReplyKeyboardRemove())
        send_welcome(message)

    elif limit_choice == '/help':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_help(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                   '19', '20')
        msg = bot.send_message(message.chat.id, 'Сколько объявлений вы хотите посмотреть?', reply_markup=markup)
        bot.register_next_step_handler(msg, posters_step_2)

    elif limit_choice == '/info':
        bot.send_message(message.chat.id, 'Хорошо, прервемся ненадолго', reply_markup=types.ReplyKeyboardRemove())
        send_info(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                   '19', '20')
        msg = bot.send_message(message.chat.id, 'Сколько объявлений вы хотите посмотреть?', reply_markup=markup)
        bot.register_next_step_handler(msg, posters_step_2)

    elif limit_choice not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
                              '17', '18', '19', '20']:
        bot.reply_to(message,
                     'Вы неверно ввели количество объявлений, которые хотите посмотреть.',
                     reply_markup=types.ReplyKeyboardRemove())
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                   '19', '20')
        msg = bot.send_message(message.chat.id, 'Сколько объявлений вы хотите посмотреть?', reply_markup=markup)
        bot.register_next_step_handler(msg, posters_step_2)
    else:
        user.limit = int(limit_choice)

        bot.send_message(message.chat.id, 'Хорошо, приступаю к поиску информации',
                         reply_markup=types.ReplyKeyboardRemove())

        get_posters(message, query=user.query, home_reg=user.home_region_num, limit=user.limit, chat_id=chat_id,
                    query_count=user.query_count)

        try:
            df = pd.read_csv(
                f"C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\query_results\\{chat_id}\\query_result__{user.query_count}__{user.query.replace('/', '').replace(':', '')}.csv",
                delimiter=',')

            df = df.replace({'EV': {'No': 'Нет', 'Yes': 'Да'}, 'mileage_rus': {'No': 'Нет', 'Yes': 'Да'},
                             'hybrid': {'No': 'Нет', 'Yes': 'Да'}, 'gas_system': {'No': 'Нет', 'Yes': 'Да'},
                             'broken': {'No': 'Нет', 'Yes': 'Да'}, 'no_doc': {'No': 'Нет', 'Yes': 'Да'},
                             'сhassis_config': {'передний': 'Передний', 'задний': 'Задний'},
                             'salesman': {'not official dealer': 'Новый от неофициального дилера',
                                          'official dealer': 'Новый от официального дилера',
                                          'owner': 'От собственника'}})
            for i in range(df.shape[0]):

                if str(df.iloc[i]['photo_url']) == 'nan':
                    photo_url = open('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\photo\\default_photo.png', 'rb')
                else:
                    photo_url = df.iloc[i]['photo_url']

                info = f'''
    <b>Марка:</b> {df.iloc[i]['brand']}
    <b>Модель:</b> {df.iloc[i]['model']}
    <b>Год:</b> {df.iloc[i]['year']}
    <b>Цвет:</b> {'Не указан' if str(df.iloc[i]['color']) == 'nan' else df.iloc[i]['color'].title()}
    <b>Поколение:</b> {'Не указано' if str(df.iloc[i]['generation']) == 'nan' else df.iloc[i]['generation']}
    <b>Рестайлинг:</b> {'Не указан' if str(df.iloc[i]['restyling']) == 'nan' else df.iloc[i]['restyling']}
    <b>Комплектация:</b> {'Не указана' if str(df.iloc[i]['configuration']) == 'nan' else df.iloc[i]['configuration'].title()}
    <b>Объем двигателя (л):</b> {'Не указан' if str(df.iloc[i]['engine_volume (liters)']) == 'nan' else df.iloc[i]['engine_volume (liters)']}
    <b>Мощность (л.с):</b> {'Не указана' if str(df.iloc[i]['hp']) == 'nan' else df.iloc[i]['hp']}
    <b>Тип топлива:</b> {'Не указан' if str(df.iloc[i]['fuel_type']) == 'nan' else df.iloc[i]['fuel_type'].title()}
    <b>Тип КПП:</b> {'Не указан' if str(df.iloc[i]['gear_type']) == 'nan' else df.iloc[i]['gear_type']}
    <b>Привод:</b> {'Не указан' if str(df.iloc[i]['сhassis_config']) == 'nan' else df.iloc[i]['сhassis_config']}
    <b>Пробег, км:</b> {'Не указан' if str(df.iloc[i]['mileage (km)']) == 'nan' else df.iloc[i]['mileage (km)']}
    <b>Без пробега по РФ:</b> {'Не указан' if str(df.iloc[i]['mileage_rus']) == 'nan' else df.iloc[i]['mileage_rus']}
    <b>Электромобиль:</b> {'Не указано' if str(df.iloc[i]['EV']) == 'nan' else df.iloc[i]['EV']}
    <b>Гибрид:</b> {'Не указано' if str(df.iloc[i]['hybrid']) == 'nan' else df.iloc[i]['hybrid']}
    <b>ГБО:</b> {'Не указано' if str(df.iloc[i]['gas_system']) == 'nan' else df.iloc[i]['gas_system']}
    <b>Руль:</b> {'Не указан' if str(df.iloc[i]['steering_wheel']) == 'nan' else df.iloc[i]['steering_wheel'].title()}
    <b>Тип кузова:</b> {'Не указан' if str(df.iloc[i]['body_type']) == 'nan' else df.iloc[i]['body_type'].title()}
    <b>Повреждения / поломки:</b> {'Не указано' if str(df.iloc[i]['broken']) == 'nan' else df.iloc[i]['broken']}
    <b>Проблемы с документами:</b> {'Не указано' if str(df.iloc[i]['no_doc']) == 'nan' else df.iloc[i]['no_doc']}
    <b>Местонахождение:</b> {'Не указано' if str(df.iloc[i]['location']) == 'nan' else df.iloc[i]['location']}
    <b>Продавец:</b> {'Не указан' if str(df.iloc[i]['salesman']) == 'nan' else df.iloc[i]['salesman']}
    <b>Цена (руб):</b> {df.iloc[i]['price (rub)']}
    <b>Налог (руб):</b> {'Не указан' if str(df.iloc[i]['tax (rub)']) == 'nan' else df.iloc[i]['tax (rub)']}
            '''

                query_hash_dict[hashlib.md5(
                    f"price_changing__{user.query_count}__{user.query.replace('/', '').replace(':', '')}__{i}".encode(
                        'utf-8')).hexdigest()] = f"price_changing__{user.query_count}__{user.query.replace('/', '').replace(':', '')}__{i}"

                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton('Посмотреть объявление', url=df.iloc[i]['URL'])
                button2 = types.InlineKeyboardButton('История изменения цены',
                                                     callback_data=hashlib.md5(
                                                         f"price_changing__{user.query_count}__{user.query.replace('/', '').replace(':', '')}__{i}".encode(
                                                             'utf-8')).hexdigest())

                markup.row(button1)
                markup.row(button2)

                np.save(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\dictionaries\\query_hash_dict.npy',
                        query_hash_dict)

                bot.send_photo(message.chat.id, photo=photo_url, caption=info, reply_markup=markup, parse_mode='html')

            brief = df[['year', 'mileage (km)', 'price (rub)', 'tax (rub)']].describe().loc[
                ['min', 'mean', 'max']].set_index(
                pd.Series(['Минимум', 'Среднее', 'Максимум']))
            brief = brief.rename(
                columns={'year': "Год выпуска", 'mileage (km)': "Пробег (км)", 'price (rub)': "Цена (руб)",
                         'tax (rub)': "Налог (руб)"})
            for i in brief.columns:
                brief[i] = brief[i].apply(lambda x: int(np.floor(x)))

            os.makedirs(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\photo\\{chat_id}',
                        exist_ok=True)

            dfi.export(brief,
                       f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\photo\\{chat_id}\\brief_info.png')

            bot.send_photo(message.chat.id, photo=open(
                f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\photo\\{chat_id}\\brief_info.png', 'rb'),
                           caption='<b>Сводная информация по вашему запросу</b>', parse_mode='html')

            user.last_queries.append(user.query)
            user.query_count = user.last_queries.count(user.query)
            np.save(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\dictionaries\\user_dict.npy',
                    user_dict)

        except:
            bot.send_message(message.chat.id,
                             'Извините, но я не смог обнаружить объявлений о продаже авто по заданным условиям. Попробуйте изменить поисковой запрос: /dialog.')


@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    hash_call_data = query_hash_dict.get(call.data)

    if 'price_changing' in hash_call_data:
        query_count = hash_call_data.split('__')[-3]
        query_result = hash_call_data.split('__')[-2]

        df = pd.read_csv(
            f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\query_results\\{call.message.chat.id}\\query_result__{query_count}__{query_result}.csv',
            delimiter=',')
        df = df.replace({'EV': {'No': 'Нет', 'Yes': 'Да'}, 'mileage_rus': {'No': 'Нет', 'Yes': 'Да'},
                         'hybrid': {'No': 'Нет', 'Yes': 'Да'}, 'gas_system': {'No': 'Нет', 'Yes': 'Да'},
                         'broken': {'No': 'Нет', 'Yes': 'Да'}, 'no_doc': {'No': 'Нет', 'Yes': 'Да'},
                         'сhassis_config': {'передний': 'Передний', 'задний': 'Задний'},
                         'salesman': {'not official dealer': 'Новый от неофициального дилера',
                                      'official dealer': 'Новый от официального дилера',
                                      'owner': 'От собственника'}})

        i = int(hash_call_data.split('__')[-1])

        driver.get('https://auto-history.info')

        search_string = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/nav/div/div[2]/form[2]/div/div/input")))

        url = df.iloc[i]['URL']
        search_string.click()
        search_string.send_keys(url)

        search_go = driver.find_element('xpath', '/html/body/div[1]/nav/div/div[2]/form[2]/div/div/span/button')
        search_go.click()

        history_info = BeautifulSoup(driver.page_source, 'html.parser')

        try:

            string = history_info.find_all('div', {'class': 'col-xs-12'})[3].find('p').get_text()

            date_price_list = re.findall(r'[\d.]+ - [\d\s]+', string)

            dates = []
            prices = []

            for j in date_price_list:
                dates.append(j.split(' - ')[0])
                prices.append(int(j.split(' - ')[1].replace(' ', '')))

            matplotlib.use("Agg")

            fig, ax = plt.subplots(1, 1, figsize=(15, 15))
            ax.plot(dates, prices, color='red', marker='o', linestyle='dotted', linewidth=2, markersize=8)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.set_xlabel('Дата', fontsize=22, va='bottom', loc="center", labelpad=30)
            ax.set_ylabel('Цена (руб)', fontsize=22, rotation=90, ha='right')
            ax.set_title('Динамика цен на данный автомобиль', fontsize=22, va='bottom')
            plt.xticks(fontsize=15, rotation=60)
            plt.yticks(fontsize=15)
            ax.grid(True)
            plt.autoscale(enable=False, axis='y')
            ax.locator_params(axis='y', integer=True)

            formatter = ticker.ScalarFormatter()
            formatter.set_scientific(False)
            ax.yaxis.set_major_formatter(formatter)

            os.makedirs(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\photo\\{call.message.chat.id}',
                        exist_ok=True)
            fig.savefig(
                f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\photo\\{call.message.chat.id}\\price_change_plot.png')

            bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                   media=types.InputMediaPhoto(open(
                                       f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\photo\\{call.message.chat.id}\\price_change_plot.png',
                                       'rb')))
        except:
            bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                   media=types.InputMediaPhoto(
                                       open('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\photo\\no_database.png',
                                            'rb')))

        query_hash_dict[hashlib.md5(
            f"photo_back__{query_count}__{query_result}__{i}".encode(
                'utf-8')).hexdigest()] = f"photo_back__{query_count}__{query_result}__{i}"

        markup1 = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Посмотреть объявление', url=df.iloc[i]['URL'])
        button2 = types.InlineKeyboardButton('Вернуть фотографию авто',
                                             callback_data=hashlib.md5(
                                                 f"photo_back__{query_count}__{query_result}__{i}".encode(
                                                     'utf-8')).hexdigest())

        markup1.row(button1)
        markup1.row(button2)

        np.save(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\dictionaries\\query_hash_dict.npy',
                query_hash_dict)

        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 caption=call.message.caption,
                                 parse_mode='html', reply_markup=markup1)
        bot.answer_callback_query(call.id)

    if 'photo_back' in hash_call_data:
        query_count = hash_call_data.split('__')[-3]
        query_result = hash_call_data.split('__')[-2]

        df = pd.read_csv(
            f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\query_results\\{call.message.chat.id}\\query_result__{query_count}__{query_result}.csv',
            delimiter=',')
        df = df.replace({'EV': {'No': 'Нет', 'Yes': 'Да'}, 'mileage_rus': {'No': 'Нет', 'Yes': 'Да'},
                         'hybrid': {'No': 'Нет', 'Yes': 'Да'}, 'gas_system': {'No': 'Нет', 'Yes': 'Да'},
                         'broken': {'No': 'Нет', 'Yes': 'Да'}, 'no_doc': {'No': 'Нет', 'Yes': 'Да'},
                         'сhassis_config': {'передний': 'Передний', 'задний': 'Задний'},
                         'salesman': {'not official dealer': 'Новый от неофициального дилера',
                                      'official dealer': 'Новый от официального дилера',
                                      'owner': 'От собственника'}})

        i = int(hash_call_data.split('__')[-1])

        if str(df.iloc[i]['photo_url']) == 'nan':
            photo_url = open('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\photo\\default_photo.png', 'rb')
        else:
            photo_url = df.iloc[i]['photo_url']

        bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id,
                               media=types.InputMediaPhoto(photo_url))

        markup2 = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Посмотреть объявление', url=df.iloc[i]['URL'])
        button2 = types.InlineKeyboardButton('История изменения цены',
                                             callback_data=hashlib.md5(
                                                 f"price_changing__{query_count}__{query_result}__{i}".encode(
                                                     'utf-8')).hexdigest())

        markup2.row(button1)
        markup2.row(button2)

        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 caption=call.message.caption,
                                 parse_mode='html', reply_markup=markup2)
        bot.answer_callback_query(call.id)


bot.infinity_polling()
