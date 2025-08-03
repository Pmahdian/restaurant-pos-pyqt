from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

def generate_invoice_pdf(invoice_data, output_path):
    """تولید فاکتور PDF برای چاپ یا ذخیره"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # استایل‌ها
    styles = getSampleStyleSheet()
    
    # --- هدر ---
    header = [
        "فاکتور فروش رستوران",
        f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}",
        "-------------------------"
    ]
    
    y_position = height - 40
    for line in header:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, line)
        y_position -= 20
    
    # --- آیتم‌ها ---
    y_position -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_position, "آیتم")
    c.drawString(200, y_position, "تعداد")
    c.drawString(300, y_position, "جمع")
    y_position -= 20
    
    c.setFont("Helvetica", 10)
    for item in invoice_data["items"]:
        c.drawString(30, y_position, item["name"])
        c.drawString(200, y_position, str(item["quantity"]))
        c.drawString(300, y_position, f"{item['price'] * item['quantity']:,}")
        y_position -= 15
    
    # --- جمع کل ---
    y_position -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_position, f"جمع کل: {invoice_data['total']:,} تومان")
    
    # --- پاورقی ---
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(30, 20, "با تشکر از خرید شما - شماره تماس: 021-12345678")
    
    c.save()