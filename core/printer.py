from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors

def generate_invoice_pdf(items, invoice_number, date, total, service_fee, discount):
    filename = f"invoice_{invoice_number}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    
    # هدر
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "فاکتور فروش رستوران")
    c.drawString(100, 780, f"شماره: {invoice_number}")
    c.drawString(100, 760, f"تاریخ: {date}")
    
    # جدول آیتم‌ها
    data = [["آیتم", "قیمت", "تعداد", "جمع"]]
    for item in items:
        data.append([
            item['name'],
            f"{item['price']:,}",
            item['quantity'],
            f"{item['price'] * item['quantity']:,}"
        ])
    
    # اضافه کردن جمع‌کل و جزئیات
    data.append(["", "", "جمع جزء:", f"{sum(item['price'] * item['quantity'] for item in items):,}"])
    data.append(["", "", "حق سرویس:", f"{service_fee:,}"])
    data.append(["", "", "تخفیف:", f"-{discount:,}"])
    data.append(["", "", "جمع نهایی:", f"{total:,}"])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    table.wrapOn(c, 400, 600)
    table.drawOn(c, 100, 600)
    
    c.save()
    return filename