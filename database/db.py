import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "restaurant.db"

def create_connection():
    """ایجاد اتصال به دیتابیس"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database():
    """ایجاد جداول دیتابیس"""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        date TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        invoice_id INTEGER,
        item_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id),
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()