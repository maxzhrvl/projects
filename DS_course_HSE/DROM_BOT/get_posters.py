import random
import re
import time
import os

import pandas as pd
import telebot
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from termcolor import colored

from secret import token

bot = telebot.TeleBot(token)


def get_posters(message, query, home_reg, limit, chat_id, query_count):
    # Словарь, на основе которого потом будет составлен набор данных:

    data = {"id": [], "brand": [], "model": [], "year": [], "color": [],
            "configuration": [], "engine_volume (liters)": [], "hp": [],
            "fuel_type": [], "gear_type": [], "сhassis_config": [],
            "mileage (km)": [], "EV": [], 'hybrid': [], "gas_system": [],
            "steering_wheel": [], "generation": [], "restyling": [],
            "price (rub)": [], "URL": [], "body_type": [], "mileage_rus": [],
            "date": [], "views_num": [], "location": [], "broken": [],
            "no_doc": [], "model_rating": [], "description": [], "with_photo": [],
            "photo_url": [], "salesman": [], "tax (rub)": []}

    # Настройки selenium:

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    s = Service('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\driver\\geckodriver.exe')
    driver = webdriver.Firefox(options=chrome_options, service=s)

    # Генератор для случая, когда необходимо перебрать все объявления в выдаче:

    #     def infinite_sequence():
    #         num = 1
    #         while True:
    #             yield num
    #             num += 1

    #     inf_seq_generator = infinite_sequence()

    # Установка домашнего региона:
    driver.get('https://www.drom.ru/my_region/?set_region={}'.format(home_reg))

    try:
        for num_page in range(1, 2):  # рассматриваем ограниченное количество страниц в выдаче (в данном случае - одну страницу)
            #   for num_page in inf_seq_generator: # для бесконечного поиска

            # Сохраняем файл (перед тем, как собирать информацию по объявлениям с новой страницы),
            # чтобы не потерять данные по уже успешно собранным страницам в случае возникновения
            # возможных ошибок
            df = pd.DataFrame(data)
            os.makedirs(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\query_results\\{chat_id}',
                        exist_ok=True)
            df.to_csv(
                f"C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\query_results\\{chat_id}\\query_result__{query_count}__{query.replace('/', '').replace(':', '')}.csv",
                index=False)

            # Заходим на страницу:
            wall_url = query + 'page{}'.format(num_page)
            time.sleep(random.random() * 2)
            driver.get(wall_url)
            bs_wall = BeautifulSoup(driver.page_source, 'html.parser')

            # Находим на ней все нужные нам объявления:

            pre_posters = bs_wall.find_all('div', {'class': 'css-1nvf6xk eaczv700'})[0]
            if len(pre_posters.find_all('div', {'data-ftid': 'bulls-list_title'})) != 0:
                posters = []
            else:
                posters = pre_posters.find_all('a', {'data-ftid': 'bulls-list_bull'})

            if len(posters) == 0:  # условие остановки бесконечной последовательности для перебора всех объявлений в выдаче
                raise StopIteration

            if len(posters) < limit:
                bot.send_message(message.chat.id,
                                 f'Извините, я не смог обнаружитьй такого количества объявлений ({limit}) о продаже'
                                 ' авто по заданным условиям, но я предоставлю Вам все, что мне удастся найти')

            for poster in posters[
                          0:limit]:  # рассматриваем каждое отдельное объявление (limit - ограничение на количество объявлений на странице)
                # Отслеживаем динамику поиска, а также возможные проблемные места:
                print(colored('Страница № {}: объявление № {}'.format(num_page, posters.index(poster) + 1),
                              attrs=['bold']), end='')
                print('\r', end='')

                # Собираем первичную информацию (без клика на объявление):

                # Год производства, марка, модель, комплектация, город

                main_info = poster.find('span', {'data-ftid': 'bull_title'}).get_text()

                data['year'].append(int(main_info.split(', ')[1]))

                try:
                    data['brand'].append(re.search(
                        r'[\w-]+((?=\sRover)|(?=\sWall)|(?=\sRomeo)|(?=\sMartin)|(?=\sKhodro)|(?=\sSamsung)|(?=\sKai)|(?=\sHower)|(?=\sавто))\s[\w]+\b\s',
                        ''.join(main_info.split(', ')[0]).strip()).group())
                except:
                    data['brand'].append(re.search(r'[\w-]+\b', ''.join(main_info.split(', ')[0]).strip()).group())

                if len(re.sub(
                        r'[\w-]+((?=\sRover)|(?=\sWall)|(?=\sRomeo)|(?=\sMartin)|(?=\sKhodro)|(?=\sSamsung)|(?=\sKai)|(?=\sHower)|(?=\sавто))\s[\w]+\b\s',
                        '',
                        ''.join(main_info.split(', ')[0]).strip())) == len(''.join(main_info.split(', ')[0]).strip()):
                    data['model'].append(re.sub(r'^[\w-]+\b\s', '', ''.join(main_info.split(', ')[0]).strip()))
                else:
                    data['model'].append(re.sub(
                        r'[\w-]+((?=\sRover)|(?=\sWall)|(?=\sRomeo)|(?=\sMartin)|(?=\sKhodro)|(?=\sSamsung)|(?=\sKai)|(?=\sHower)|(?=\sавто))\s[\w]+\b\s',
                        '',
                        ''.join(main_info.split(', ')[0]).strip()))

                try:
                    data['configuration'].append(poster.find('div', {'class': 'css-o2r31p e3f4v4l0'}).get_text())
                except:
                    data['configuration'].append('NaN')

                try:
                    data['location'].append(poster.find('span', {'data-ftid': 'bull_location'}).get_text())
                except:
                    data['location'].append('NaN')

                # Мощность и объём двигателя, цена

                additional_info = poster.find_all('span', {'data-ftid': 'bull_description-item'})

                try:
                    data['engine_volume (liters)'].append(float(re.search(r'^\b[\d.]+\b(?! л.с.)(?= л)',
                                                                          additional_info[0].get_text()).group()))
                except:
                    data['engine_volume (liters)'].append('NaN')

                try:
                    data['hp'].append(int(re.search(r'\d+(?= л.с.)', additional_info[0].get_text()).group()))
                except:
                    data['hp'].append('NaN')

                try:
                    data['price (rub)'].append(int(poster.find('span', {'data-ftid': 'bull_price'}).
                                                   get_text().replace('\xa0', '')))
                except:
                    data['price (rub)'].append('NaN')

                # Информация о продавце

                try:
                    if poster.find('div', {'class': 'css-xbntwf eha7c1r0'}).get_text().strip().replace(
                            'без пробега по РФ', '') == 'новый от неофициального дилера':
                        data['salesman'].append('not official dealer')
                    elif poster.find('div', {'class': 'css-xbntwf eha7c1r0'}).get_text().strip().replace(
                            'без пробега по РФ', '') == 'новый':
                        data['salesman'].append('official dealer')
                    elif poster.find('div', {'class': 'css-xbntwf eha7c1r0'}).get_text().strip().replace(
                            'без пробега по РФ', '') == 'от собственника':
                        data['salesman'].append('owner')
                    else:
                        data['salesman'].append('NaN')
                except:
                    data['salesman'].append('NaN')

                # Собираем вторичную информацию (по клику на объявление):

                poster_url = poster.get('href')  # ссылка на объявление
                data["URL"].append(poster_url)
                time.sleep(random.random() * 2)
                driver.get(poster_url)  # переходим драйвером по ссылке
                bs_poster = BeautifulSoup(driver.page_source, 'html.parser')
                brief_info = bs_poster.find('table', {'class': 'css-xalqz7 eppj3wm0'}).find_all('tr')

                char_list = []  # список для сбора характеристик, которые удается найти

                # Тип топлива, тип коробки передач, колёсная формула, гибридная установка, электромобиль,
                # тип коробки передач, колёсная формула, ГБО, цвет, пробег, расположение руля, поколение,
                # рестайлинг, тип кузова, пробег по РФ, дата размещения объявления, количество просмотров,
                # особые отметки (поломки / проблемные документы), рейтинг модели,
                # наличие фото в объявлении и ссылка на фото, налог

                for j in range(0, len(brief_info)):

                    try:

                        char_list.append(brief_info[j].find('th').get_text())

                        if brief_info[j].find('th').get_text() == 'Коробка передач':
                            if brief_info[j].find('td').get_text() == 'автомат':  # если пользователь не указал,
                                # какой именно у него тип автоматической коробки (АКПП, робот, вариатор),
                                # то присваевается значение "АКПП"
                                data['gear_type'].append('АКПП')
                            else:
                                data['gear_type'].append(brief_info[j].find('td').get_text())

                        if brief_info[j].find('th').get_text() == 'Привод':
                            data['сhassis_config'].append(brief_info[j].find('td').get_text())

                        if brief_info[j].find('th').get_text() == 'Двигатель':
                            if brief_info[j].find('td').get_text().split(', ')[0] not in ['бензин', 'дизель']:
                                data['fuel_type'].append('NaN')
                            else:
                                data['fuel_type'].append(brief_info[j].find('td').get_text().split(', ')[0])
                            if "ГБО" not in brief_info[j].find('td').get_text().split(', '):
                                data['gas_system'].append('No')
                            else:
                                data['gas_system'].append('Yes')
                            if "гибрид" not in brief_info[j].find('td').get_text().split(', '):
                                data['hybrid'].append('No')
                            else:
                                data['hybrid'].append('Yes')
                            if "электро" not in brief_info[j].find('td').get_text().split(', '):
                                data['EV'].append('No')
                            else:
                                data['EV'].append('Yes')

                        if brief_info[j].find('th').get_text() == 'Тип кузова':
                            data['body_type'].append(brief_info[j].find('td').get_text())

                        if brief_info[j].find('th').get_text() == "Цвет":
                            data['color'].append(brief_info[j].find('td').get_text())

                        if brief_info[j].find('th').get_text() == "Пробег, км" or brief_info[j].find(
                                'th').get_text() == "Пробег":
                            if brief_info[j].find('td').get_text().split(', ')[0].replace("\xa0",
                                                                                          ' ') == "новый автомобиль":
                                data['mileage (km)'].append(0)
                                data['mileage_rus'].append('No')
                            elif brief_info[j].find('td').get_text().split(', ')[0].replace("\xa0",
                                                                                            ' ') == "без пробега по РФ":
                                data['mileage (km)'].append('NaN')
                                data['mileage_rus'].append('Yes')
                            else:
                                try:
                                    data['mileage (km)'].append(int(re.search(r'\d+(?=, )', brief_info[j].find('td').
                                                                              get_text().replace("\xa0", '')).group()))
                                    data['mileage_rus'].append('Yes')
                                except:
                                    data['mileage (km)'].append(
                                        int(brief_info[j].find('td').get_text().replace("\xa0", '')))
                                    data['mileage_rus'].append('No')

                        if brief_info[j].find('th').get_text() == "Руль":
                            data['steering_wheel'].append(brief_info[j].find('td').get_text())

                        if brief_info[j].find('th').get_text() == "Поколение":

                            generation_restyling_info = brief_info[j].find('td').get_text().strip()

                            try:
                                сheck_1_restyling = generation_restyling_info.split(', ')[1]
                                data['generation'].append(generation_restyling_info.split(', ')[0].split(' ')[0])

                                try:
                                    check_2_restyling = generation_restyling_info.split(', ')[1].split(' ')[1]
                                    data['restyling'].append(generation_restyling_info.split(', ')[1].split(' ')[0])

                                except:
                                    data['restyling'].append(1)

                            except:
                                data['generation'].append(generation_restyling_info.split(' ')[0])
                                data['restyling'].append('NaN')

                        if brief_info[j].find('th').get_text() == "Особые отметки":
                            try:
                                if brief_info[j].find('td').get_text().split(', ')[1] == 'документы с проблемами' or \
                                        brief_info[j].find('td').get_text().split(', ')[
                                            1] == 'документы с проблемами или отсутствуют':
                                    data['no_doc'].append('Yes')
                                    data['broken'].append('Yes')
                                elif brief_info[j].find('td').get_text().split(', ')[0] == 'документы с проблемами' or \
                                        brief_info[j].find('td').get_text().split(', ')[
                                            0] == 'документы с проблемами или отсутствуют':
                                    data['no_doc'].append('Yes')
                                    data['broken'].append('No')
                            except:
                                if brief_info[j].find('td').get_text().split(', ')[
                                    0] == 'требуется ремонт или не на ходу':
                                    data['broken'].append('Yes')
                                    data['no_doc'].append('No')
                                else:
                                    data['broken'].append('No')
                                    data['no_doc'].append('Yes')

                    except:
                        continue

                if "Коробка передач" not in char_list:
                    data['gear_type'].append('NaN')
                if "Привод" not in char_list:
                    data['сhassis_config'].append('NaN')
                if "Двигатель" not in char_list:
                    data['fuel_type'].append('NaN')
                    data['gas_system'].append('NaN')
                    data['hybrid'].append('NaN')
                    data['EV'].append('NaN')
                if "Руль" not in char_list:
                    data['steering_wheel'].append('NaN')
                if "Цвет" not in char_list:
                    data['color'].append('NaN')
                if "Пробег, км" not in char_list and "Пробег" not in char_list:
                    data['mileage (km)'].append('NaN')
                    data['mileage_rus'].append('NaN')
                if "Поколение" not in char_list:
                    data['generation'].append('NaN')
                    data['restyling'].append('NaN')
                if "Тип кузова" not in char_list:
                    data['body_type'].append('NaN')
                if "Особые отметки" not in char_list:
                    data['broken'].append('No')
                    data['no_doc'].append('No')

                try:
                    identification_info = bs_poster.find('div', {'class': 'css-48ojaj e1lm3vns0'}).find('div', {
                        'class': 'css-pxeubi evnwjo70'})
                    data['id'].append(int(identification_info.get_text().split(' ')[1]))
                    data['date'].append(identification_info.get_text().split(' ')[3])
                except:
                    data['id'].append('NaN')
                    data['date'].append('NaN')

                try:
                    views_info = bs_poster.find('div', {'class': 'css-48ojaj e1lm3vns0'}).find('div', {
                        'class': 'css-14wh0pm e1lm3vns0'})
                    data['views_num'].append(int(views_info.get_text().replace(' ', '')))
                except:
                    data['views_num'].append('NaN')

                try:
                    data['model_rating'].append(float(bs_poster.find('div', {'data-ftid': "component_rating"}).
                                                      get_text().replace('оценка модели', '')))
                except:
                    data['model_rating'].append('NaN')

                try:
                    if bs_poster.find('div', {'class': 'css-1j8ksy7 eotelyr0'}).find('span', {
                        'class': 'css-1kb7l9z e162wx9x0'}).get_text() == 0:
                        data['description'].append('No')
                    else:
                        data['description'].append('Yes')
                except:
                    data['description'].append('No')

                try:
                    data['photo_url'].append(
                        bs_poster.find('div', {'data-ftid': 'bull-page_bull-gallery_photos-collapsed'}).find('div', {
                            'class': 'css-bjn8wh ecmc0a90'}).find('a').get('href'))
                    data['with_photo'].append('Yes')
                except:
                    data['photo_url'].append('NaN')
                    data['with_photo'].append('No')

                try:
                    driver.find_element('xpath',
                                        '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td/span/button').click()
                    tax_info = BeautifulSoup(driver.page_source, 'html.parser')
                    data['tax (rub)'].append(
                        int(tax_info.find('span', {'class': 'css-1h5ys6r e162wx9x0'}).get_text().replace(' ',
                                                                                                         '').replace(
                            '₽', '')))
                except:
                    data['tax (rub)'].append('NaN')

                if posters.index(poster) == 0:
                    msg = bot.send_message(message.chat.id, 'Я собрал информацию по объявлению <b>№ {}</b>'.format(
                        posters.index(poster) + 1), parse_mode='html')
                elif posters.index(poster) == limit - 1:
                    txt = '''
Я собрал информацию по объявлению <b>№ {}</b>.
Сбор информации завершен.
                    '''.format(posters.index(poster) + 1)
                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=txt, parse_mode='html')
                else:
                    txt = 'Я собрал информацию по объявлению <b>№ {}</b>'.format(posters.index(poster) + 1)
                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=txt, parse_mode='html')

            # Сохраняем файл на случай, если в выдаче не более одной страницы:
            df = pd.DataFrame(data)
            os.makedirs(f'C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\query_results\\{chat_id}',
                        exist_ok=True)
            df.to_csv(
                f"C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\user_data\\query_results\\{chat_id}\\query_result__{query_count}__{query.replace('/', '').replace(':', '')}.csv",
                index=False)

    except StopIteration:  # остановка бесконечной последовательности для перебора всех страниц в выдаче / или условие того, что объявлений не нашлось на странице
        print('\nPages are already over!')

# bot.infinity_polling()
