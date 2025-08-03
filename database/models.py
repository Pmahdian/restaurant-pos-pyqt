from datetime import datetime
from .db import create_connection

class Item:
    def __init__(self, name, price, id=None):
        self.id = id
        self.name = name
        self.price = price

    def save(self):
        conn = create_connection()
        cursor = conn.cursor()
        if self.id:
            cursor.execute("UPDATE items SET name=?, price=? WHERE id=?", 
                         (self.name, self.price, self.id))
        else:
            cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)",
                         (self.name, self.price))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

class Customer:
    # مشابه کلاس Item پیاده‌سازی شود
    pass

class Invoice:
    # پیاده‌سازی مدیریت فاکتورها
    pass