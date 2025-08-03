from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors

def generate_invoice_pdf(invoices, filename):
    """تولید PDF برای گزارش روزانه"""
    c = canvas.Canvas(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # عنوان گزارش
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "گزارش فروش روزانه")
    c.drawString(100, 780, f"تاریخ: {invoices[0]['date'][:10]}")
    
    # جمع کل روز
    daily_total = sum(inv["total"] for inv in invoices)
    c.drawString(100, 760, f"جمع کل روز: {daily_total:,} تومان")
    
    # جدول فاکتورها
    data = [["شماره", "تاریخ", "تعداد آیتم", "جمع فاکتور"]]
    
    for inv in invoices:
        data.append([
            str(inv["id"]),
            inv["date"][11:16],  # فقط ساعت
            str(len(inv["items"])),
            f"{inv['total']:,}"
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    table.wrapOn(c, 400, 600)
    table.drawOn(c, 100, 600)
    c.save()