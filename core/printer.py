from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors

def generate_invoice_pdf(items, filename, invoice_number):
    """تولید فاکتور PDF برای مشتری"""
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # هدر فاکتور
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "فاکتور فروش رستوران")
    c.drawString(100, 780, f"شماره: {invoice_number}")
    c.drawString(100, 760, f"تاریخ: {invoice_number}")
    
    # خط جداکننده
    c.line(100, 750, 500, 750)
    
    # آیتم‌ها
    y_position = 720
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_position, "آیتم")
    c.drawString(300, y_position, "تعداد")
    c.drawString(400, y_position, "جمع")
    y_position -= 20
    
    c.setFont("Helvetica", 10)
    for item in items:
        c.drawString(100, y_position, item["name"])
        c.drawString(300, y_position, str(item["quantity"]))
        c.drawString(400, y_position, f"{item['price'] * item['quantity']:,}")
        y_position -= 15
    
    # محاسبات نهایی
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    y_position -= 20
    c.line(100, y_position, 500, y_position)
    y_position -= 20
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y_position, "جمع کل:")
    c.drawString(400, y_position, f"{subtotal:,} تومان")
    
    # پاورقی
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(100, 30, "با تشکر از خرید شما - شماره تماس: 021-12345678")
    
    c.save()