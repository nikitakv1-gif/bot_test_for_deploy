from bs4 import BeautifulSoup as bs4
import requests
import time

link = 'https://irecommend.ru/catalog/list/22'
link_main = 'https://irecommend.ru'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "ru-RU,ru;q=0.9",
}


def get_companys(link):
	''' В скрипт передается ссылка на сферу из которой будем парсить отзывы для обучения'''
	h = {}
	try:
	    response = requests.get(link, headers=headers, timeout=10)
	    soup = bs4(response.text, 'lxml')  # Вывод первых 500 символов
	    bank_products = soup.find_all('div', class_ = 'title')
	    for i in bank_products:
	    	i = i.find('a')
	    	h[i.text] = i.get('href')
	except Exception as e:
	    print(f"Ошибка: {e}")

	return h


def get_reviews(h):
	h_l = list(h.keys())
	link_to = link_main + h[h_l[0]]
	response = requests.get(link_to)
	soup = bs4(response.text, 'lxml')
	print(soup.prettify())

get_reviews(get_companys(link))