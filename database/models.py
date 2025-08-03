from datetime import datetime
import sqlite3

MENU = {
    "پیش‌غذا": [
        {"id": 1, "name": "سالاد فصل", "price": 25000},
        {"id": 2, "name": "سوپ قارچ", "price": 18000},
    ],
    # ... (بقیه منو مثل قبل)
}

def save_invoice_to_db(items, total, service_fee, discount):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    # ایجاد جدول اگر وجود نداشته باشد
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        total REAL NOT NULL,
        service_fee REAL NOT NULL,
        discount REAL NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoice_items (
        invoice_id INTEGER,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id)
    )
    ''')
    
    # ذخیره فاکتور
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO invoices (date, total, service_fee, discount) VALUES (?, ?, ?, ?)",
        (date, total, service_fee, discount)
    )
    invoice_id = cursor.lastrowid
    
    # ذخیره آیتم‌های فاکتور
    for item in items:
        cursor.execute(
            "INSERT INTO invoice_items VALUES (?, ?, ?, ?)",
            (invoice_id, item['name'], item['quantity'], item['price'])
        )
    
    conn.commit()
    conn.close()
    return invoice_id