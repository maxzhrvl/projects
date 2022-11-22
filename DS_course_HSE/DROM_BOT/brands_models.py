import time
from bs4 import BeautifulSoup
import numpy as np

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

chrome_options = Options()
chrome_options.add_argument("--headless")
s = Service('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\driver\\geckodriver.exe')
driver = webdriver.Firefox(options=chrome_options, service=s)

driver.get('https://www.drom.ru/catalog/')
time.sleep(5)
driver.find_element('css selector', 'body > div:nth-child(3) > div.css-imk91o.e1m0rp600 > div.css-1ojz5p3.e1m0rp601 > div.css-0.e1m0rp602 > div.css-18clw5c.ehmqafe0 > div:nth-child(4) > div.css-1qm0fmp.e1lm3vns0 > div > span > div').click()
time.sleep(5)

models = {}

brands_list = BeautifulSoup(driver.page_source, 'html.parser').find_all('a', {'data-ftid': 'component_cars-list-item_hidden-link'})

for i in brands_list:
    models.update({i.get_text().lower(): [i.get('href').split('/')[-2], i.get_text(), {}]})
    driver.get(i.get('href'))
    time.sleep(5)
    models_list = BeautifulSoup(driver.page_source, 'html.parser').find_all('a', {'class': 'e64vuai0 css-1i48p5q e104a11t0'})
    for j in models_list:
        models[i.get_text().lower()][2].update({j.get_text().lower(): [j.get('href').split('/')[-2], j.get_text()]})

np.save('C:\\Users\\zhmax\\PycharmProjects\\Drom_bot\\basic_dictionaries\\brands_models_dict.npy', models)
