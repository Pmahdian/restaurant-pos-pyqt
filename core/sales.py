from datetime import date
from database.db import create_connection

def get_daily_sales(report_date=None):
    """گزارش فروش روزانه"""
    if not report_date:
        report_date = date.today().isoformat()
    
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT i.id, i.date, c.name, i.total 
    FROM invoices i
    LEFT JOIN customers c ON i.customer_id = c.id
    WHERE date(i.date) = date(?)
    """, (report_date,))
    
    sales = cursor.fetchall()
    conn.close()
    
    return sales