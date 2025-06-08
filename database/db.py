import sqlite3
import datetime
from flask import g, current_app

DATABASE = 'reviews_nps.sqlite'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

class DataBase:
    def __init__(self, table_name):
        self.table_name = table_name
        self.db = get_db()
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    text TEXT,
                                    plus TEXT,
                                    minus TEXT,
                                    model_score INTEGER,
                                    user_score INTEGER,
                                    date_time DATETIME
                                )""")
        self.db.commit()

    def append_table(self, text, plus, minus, model_score, user_score):
        now = datetime.datetime.now().isoformat()
        text = text[2:len(text)-2]
        plus = plus[2:len(plus)-2]
        minus = minus[2:len(minus)-2]
        self.cursor.execute(f"""INSERT INTO {self.table_name} 
                                (text, plus, minus, model_score, user_score, date_time)
                                VALUES (?, ?, ?, ?, ?, ?)""",
                            (text, plus, minus, int(model_score), user_score, now))
        self.db.commit()
