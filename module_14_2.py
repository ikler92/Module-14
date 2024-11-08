import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('not_telegram.db')
cursor = conn.cursor()

# Создание таблицы Users (если она ещё не существует)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER,
    balance INTEGER NOT NULL
)
''')

# Удаление пользователя с id = 6
cursor.execute('DELETE FROM Users WHERE id = 6')

# Подсчёт общего количества пользователей
cursor.execute('SELECT COUNT(*) FROM Users')
total_users = cursor.fetchone()[0]

# Подсчёт суммы всех балансов
cursor.execute('SELECT SUM(balance) FROM Users')
all_balances = cursor.fetchone()[0]

# Вывод среднего баланса всех пользователей
if total_users > 0:
    print(all_balances / total_users)
else:
    print("Нет пользователей для вычисления среднего баланса.")

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()
