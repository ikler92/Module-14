import sqlite3

# Функция для инициализации базы данных и создания таблицы Products
def initiate_db():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Функция для получения всех продуктов из таблицы Products
def get_all_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, price FROM Products')
    products = cursor.fetchall()
    conn.close()
    return products
