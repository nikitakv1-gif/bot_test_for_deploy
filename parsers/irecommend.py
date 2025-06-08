from bs4 import BeautifulSoup as bs4
import requests
import time

link = 'https://irecommend.ru/catalog/list/22'
link_main = 'https://irecommend.ru'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

class Irecommend:
	def __init__(self, main_link):
		self.main_link = main_link

	def get_rew(self, input_link):
		review_links = []

		t = requests.get(input_link).text

		print(t)
		
		for t in bs4(t, "lxml").find_all('a', {"class": 'reviewTextSnippet'}):
			back = t['href']
			print(self.main_link+back)
			print(requests.get(self.main_link+back).text)

		# with open(r"D:\University\Samsung\project\parsers\ireccomend_links.txt", 'a') as f:
		# 	for t in bs4(t).find_all('a', {"class": 'reviewTextSnippet'}):
		# 		f.write(t['href'])
		# 		f.write('\n')



d = Irecommend(link_main)
d.get_rew(r'https://irecommend.ru/content/tinkoff')
