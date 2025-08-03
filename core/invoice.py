from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
from database.models import Invoice

def generate_pdf_receipt(invoice_id):
    """تولید فاکتور PDF"""
    invoice = Invoice.get_by_id(invoice_id)
    if not invoice:
        return None
    
    filename = f"receipt_{invoice_id}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    
    # هدر فاکتور
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "فاکتور فروش رستوران")
    c.drawString(100, 780, f"شماره فاکتور: {invoice_id}")
    c.drawString(100, 760, f"تاریخ: {invoice.date}")
    
    # جزئیات مشتری
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"مشتری: {invoice.customer.name}")
    
    # آیتم‌های سفارش
    y_position = 700
    c.drawString(100, y_position, "ردیف | نام آیتم | تعداد | قیمت واحد | جمع")
    y_position -= 20
    
    for index, item in enumerate(invoice.items, start=1):
        c.drawString(100, y_position, 
                    f"{index} | {item.name} | {item.quantity} | {item.price} | {item.total}")
        y_position -= 20
    
    # جمع کل
    c.drawString(100, y_position - 30, f"جمع کل: {invoice.total}")
    
    c.save()
    return filename