from datetime import datetime
import sqlite3

MENU = {

    "سوسیس ": [
        {"id": 1, "name": " کوکتل", "price": 70000},
        {"id": 2, "name": "کوکتل پنیری ", "price": 83000},
        {"id": 3, "name": " آلمانی ", "price": 63000},
        {"id": 4, "name": " بندری ", "price": 85000},
        {"id": 5, "name": " هات داگ ", "price": 80000},
    ],


    "ساندویچ": [
      
        {"id": 6, "name": " فلافل ", "price": 65000},
        {"id": 7, "name": " فلافل ویژه ", "price": 90000},
        {"id": 8, "name": " ماکارونی ", "price": 97000},
        {"id": 9, "name": " زبان", "price": 248000},
        {"id": 10, "name": "مغز  ", "price": 198000},
        {"id": 11, "name": " مغز و زبان", "price": 248000},
        {"id": 12, "name": "ژامبون سرد ", "price": 136000},
        {"id": 14, "name": " مارتادلا ", "price": 72000},
        {"id": 15, "name": " جگر ", "price": 85000},
        {"id": 16, "name": " مرغ ", "price": 98000},
        {"id": 17, "name": " تخم مرغ آب‌پز ", "price": 63000},
        
    ],
    "برگر ": [
        {"id": 18, "name": "برگر کلاسیک ", "price": 214000},
        {"id": 19, "name": "ماشروم برگر ", "price": 237000},
        {"id": 20, "name": "چیز برگر ", "price": 226000},
        {"id": 21, "name": " دبل برگر", "price": 314000},
        
    ],

    "پرسی ": [
        {"id": 22, "name": " گوجه و خیارشور", "price": 47000},
        {"id": 23, "name": " ماکارونی پرسی", "price": 187000},
        {"id": 24, "name": " بندری پرسی", "price": 175000},
        {"id": 25, "name": " فلافل پرسی", "price": 162000},
      
        
    ],
    "نوشیدنی ": [
        {"id": 23, "name": " دوغ", "price": 35000},
        {"id": 24, "name": " نوشابه زرد", "price": 35000},
        {"id": 25, "name": " نوشابه مشکی", "price": 35000},
        {"id": 26, "name": " نوشابه اسپرایت", "price": 35000},
        {"id": 27, "name": " آب", "price": 10000}
        
    ],
   


}
def save_invoice_to_db(items, total, service_fee, discount):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    # ایجاد جداول با ساختار جدید
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id)
    )
    ''')
    
    # بررسی وجود ستون description و اضافه کردن اگر وجود نداشت
    cursor.execute("PRAGMA table_info(invoice_items)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'description' not in columns:
        cursor.execute("ALTER TABLE invoice_items ADD COLUMN description TEXT")
    
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO invoices (date, total, service_fee, discount) VALUES (?, ?, ?, ?)",
        (date, total, service_fee, discount)
    )
    invoice_id = cursor.lastrowid
    
    for item in items:
        cursor.execute(
            "INSERT INTO invoice_items (invoice_id, item_name, quantity, price, description) VALUES (?, ?, ?, ?, ?)",
            (
                invoice_id, 
                item['name'], 
                item['quantity'], 
                item['price'], 
                item.get('description', '')
            )
        )
    
    conn.commit()
    conn.close()
    return invoice_id