from bs4 import BeautifulSoup
import re
import copy
import numpy as np
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

chrome_options = Options()
chrome_options.add_argument("--headless")
s = Service('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\driver\\geckodriver.exe')
driver = webdriver.Firefox(options=chrome_options, service=s)

cities_wall_url = 'https://auto.drom.ru/cities/'
driver.get(cities_wall_url)
bs_cities_wall = BeautifulSoup(driver.page_source, 'html.parser')

location = {}
cities = {}

for i in bs_cities_wall.find_all('noscript')[1:-3]: # на уровне всех регионов
    for j in i: # на уровне одного региона
        if j != '\n':
            if 'region' in j.get('href'):
                rus_region_name = j.get_text().lower()
                region_num = int(re.search(r'(?<=https://auto.drom.ru/region)\d+', j.get('href')).group())
                location.update({rus_region_name: [region_num, j.get_text()]})
            elif 'https://moscow' in j.get('href'):
                rus_region_name = j.get_text().lower()
                region_num = int(77)
                location.update({rus_region_name: [region_num, j.get_text()]})
                cities.update({'москва': ['moscow', j.get_text()]})
                cities_copied = copy.deepcopy(cities)
            elif 'spb' in j.get('href'):
                rus_region_name = j.get_text().lower()
                region_num = int(78)
                location.update({rus_region_name: [region_num, j.get_text()]})
                cities.update({'санкт-петербург': ['spb', j.get_text()]})
                cities_copied = copy.deepcopy(cities)
            else:
                eng_city_name = re.search(r'(?<=https://)[\w\s-]+(?=.drom.ru/auto/)', j.get('href')).group().lower()
                rus_city_name = j.get_text().lower()
                cities.update({rus_city_name: [eng_city_name, j.get_text()]})
                cities_copied = copy.deepcopy(cities)
        else:
            continue
    cities.clear()
    location[rus_region_name].append(cities_copied)

np.save('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\basic_dictionaries\\regions_cities_dict.npy', location)
