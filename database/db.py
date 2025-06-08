import psycopg2
import psycopg2.extras
import datetime
from flask import g
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_CONFIG = {
    'dbname': os.getenv('dbname'),
    'user': os.getenv('user'),
    'password': os.getenv('password'),
    'host': os.getenv('host'), 
    'port': os.getenv('port')
}

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(**DATABASE_CONFIG)
        g.db.autocommit = True  # Можно ставить, чтобы не вызывать commit вручную
        g.cursor = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return g.db, g.cursor

def close_db(e=None):
    cursor = g.pop('cursor', None)
    if cursor is not None:
        cursor.close()
    db = g.pop('db', None)
    if db is not None:
        db.close()

class DataBase:
    def __init__(self, table_name):
        self.table_name = table_name
        self.db, self.cursor = get_db()
        self.create_table()

    def create_table(self):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                                    id SERIAL PRIMARY KEY,
                                    text TEXT,
                                    plus TEXT,
                                    minus TEXT,
                                    model_score INTEGER,
                                    user_score INTEGER,
                                    date_time TIMESTAMP
                                )""")
        # если autocommit=False, вызвать self.db.commit()

    def append_table(self, text, plus, minus, model_score, user_score):
        now = datetime.datetime.now()
        text = text[2:len(text)-2]
        plus = plus[2:len(plus)-2]
        minus = minus[2:len(minus)-2]
        self.cursor.execute(f"""INSERT INTO {self.table_name} 
                                (text, plus, minus, model_score, user_score, date_time)
                                VALUES (%s, %s, %s, %s, %s, %s)""",
                            (text, plus, minus, int(model_score), user_score, now))
        # если autocommit=False, вызвать self.db.commit()
