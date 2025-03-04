import sqlite3
import logging
logger = logging.getLogger(__name__)


# 📌 Подключение к БД и создание таблицы, если её нет
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT,
        phone TEXT,
        city TEXT
    )
''')

conn.commit()
conn.close()

# 📌 Функция для добавления нового пользователя
async def add_user(user_id, username, full_name, phone, city):
    logger.info(f"🔍 add_user вызывается для: {user_id}, {username}, {full_name}, {phone}, {city}")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, full_name, phone, city)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, full_name, phone, city))

    conn.commit()
    conn.close()

# 📌 Функция для получения информации о пользователе
def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user
