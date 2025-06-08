import time
import csv
import random
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import sqlite3
import datetime 

class DataBase:
    def __init__(self):
        self.table_name = 'train_data'
        self.db = sqlite3.connect('reviews_nps.sqlite')
        self.cursor = self.db.cursor()
        # self.create_table()

    def create_table(self):
        self.cursor.execute(f""" DROP TABLE IF EXISTS {self.table_name}""")
        self.cursor.execute(f"""CREATE TABLE {self.table_name} (
                                    subject String,
                                    url String,
                                    author String,
                                    date String,
                                    rating Int,
                                    title String,
                                    content String,
                                    pros String,
                                    cons String,
                                    source String
                                )""")
        self.db.commit()

    def append_table(self, subject, url, author, date, rating, title, content, pros, cons, source):
        if isinstance(title, tuple):
            title = title[0] if title else ""
        
        # Safely convert rating to integer
        try:
            rating_int = int(rating) if rating and str(rating).strip().isdigit() else None
        except (ValueError, TypeError):
            rating_int = None
        
        # Debug print to check values before insertion
        
        # Insert into the database
        self.cursor.execute(f"""INSERT INTO {self.table_name} 
                            (subject, url, author, date, rating, title, content, pros, cons, source)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (subject, url, author, date, rating_int, title, content, pros, cons, source))
        self.db.commit()



class OtzovikParser:
    def __init__(self):
        self.driver = None
        self.ua = UserAgent()
        self._init_driver()
        
    def _init_driver(self):
        """Инициализация драйвера с актуальными настройками"""
        options = uc.ChromeOptions()

        # Базовые настройки
        options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")

        # Дополнительные обходные меры
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")

        try:
            # Просто создаем экземпляр драйвера (без driver_executable_path и прочего)
            self.driver = uc.Chrome(options=options)

            # Настройки ожидания и таймаута
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(5)

        except Exception as e:
            print(f"Ошибка инициализации драйвера: {e}")
            raise


    def _human_delay(self):
        """Имитация человеческой задержки"""
        time.sleep(random.uniform(0.7, 3.2))
        
    def get_page(self, url: str, retries: int = 3) -> bool:
        """Загрузка страницы с повторными попытками"""
        for attempt in range(retries):
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
                self._human_delay()
                return True
            except Exception as e:
                print(f"Попытка {attempt+1}/{retries} ошибка: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(5)
                    continue
                return False

    def parse_reviews(self, subject: str, start_page = 1,  max_pages: int = 3) -> List[Dict]:
        """Парсит отзывы с указанного количества страниц"""
        base_url = f"https://otzovik.com/reviews/{subject}/"
        reviews = []
        
        for page in range(start_page, max_pages + 1):
            print(f"Обработка страницы {page}...")
            page_url = f"{base_url}{page}/" if page > 1 else base_url
            
            if not self.get_page(page_url):
                continue
            
            try:
                # Прокрутка для загрузки всех элементов
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1, 3))
                
                # Получаем все блоки отзывов
                review_items = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.item.status4.mshow0')))
                
                for item in review_items:
                    try:
                        self.parse_review_item(item, subject)
                    except Exception as e:
                        print(f"Ошибка парсинга отзыва: {str(e)}")
                        continue
                    
                time.sleep(random.uniform(3, 7))
                
            except Exception as e:
                print(f"Ошибка обработки страницы {page}: {str(e)}")
                continue
    def parse_review_item(self, item, subject: str):
        """Парсит отдельный отзыв"""
        try:
            print('Открываем')
            print(item)
            # Кликаем на кнопку "Читать отзыв"
            read_btn = item.find_element(By.CSS_SELECTOR, 'a.review-btn.review-read-link')
            review_url = read_btn.get_attribute('href')

            # Открываем отзыв в новой вкладке
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(review_url)
            
            # Ждем загрузки страницы отзыва
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.item.review-wrap')))
            
            # Парсим данные отзыва
            subject = subject
            url = review_url
            author = self.driver.find_element(By.CSS_SELECTOR, 'a.user-login').text.strip()
            date = self.driver.find_element(By.CSS_SELECTOR, 'abbr.value').get_attribute('title')
            rating = self.driver.find_element(
                By.CSS_SELECTOR, 'div.rating-score.tooltip-right').get_attribute('title').split(':')[1].strip()
            title = self.driver.find_element(By.TAG_NAME, 'h1').text.strip(),
            content = self.driver.find_element(
                By.CSS_SELECTOR, 'div.review-body.description').text.strip().replace('"', '')
            pros = self.driver.find_element(
                By.CSS_SELECTOR, 'div.review-plus').text.strip().split(":")[1].strip().replace('"', '') if self.driver.find_elements(
                By.CSS_SELECTOR, 'div.review-plus') else ""
            cons = self.driver.find_element(
                By.CSS_SELECTOR, 'div.review-minus').text.strip().split(":")[1].strip().replace('"', '') if self.driver.find_elements(
                By.CSS_SELECTOR, 'div.review-minus') else ""
            source = 'otzovik.com'
            
            # Закрываем вкладку с отзывом и возвращаемся
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(random.uniform(1, 3))
            
            db.append_table(subject, url, author, date, rating, title, content, pros, cons, source)
        except Exception as e:
            print(f"Ошибка обработки отзыва: {str(e)}")
            # Восстанавливаем состояние драйвера при ошибках
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            return None
        return reviews
    def save_to_csv(self, data: List[Dict], filename: str):
        """Сохранение результатов в CSV"""
        if not data:
            print("Нет данных для сохранения")
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"Данные сохранены в {filename}")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def close(self):
        """Корректное закрытие драйвера"""
        if self.driver:
            self.driver.quit()
            self.driver = None

if __name__ == "__main__":
    parser = None
    db = DataBase()
    try:
        parser = OtzovikParser()
        reviews = parser.parse_reviews("bank_vtb_24", 90, max_pages=141)
        parser.save_to_csv(reviews, "reviews.csv")
        print(f"Получено {len(reviews)} отзывов")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        if parser:
            parser.close()
            
            