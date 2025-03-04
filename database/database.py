import sqlite3

# 📌 Подключение к БД (или создание)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# 📌 Создаём таблицу, если её нет
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

# 📌 Сохранение изменений
conn.commit()
conn.close()


# 📌 Функция для проверки, зарегистрирован ли пользователь
def is_user_registered(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user is not None  # ✅ Вернёт True, если пользователь есть в БД, иначе False


# 📌 Функция для добавления нового пользователя
def add_user(user_id, username, full_name, phone=None, city=None):
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
