from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from datetime import datetime
import os

def generate_invoice_pdf(invoices, output_path):
    """تولید PDF حرفه‌ای برای گزارش فروش روزانه"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # استایل‌های پایه
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # وسط چین
    
    # --- هدر گزارش ---
    title = Paragraph(f"<b>گزارش فروش روزانه رستوران</b>", title_style)
    title.wrapOn(c, width-100, 50)
    title.drawOn(c, 50, height-50)
    
    # اطلاعات تاریخ و شماره
    c.setFont("Helvetica", 10)
    c.drawRightString(width-50, height-40, f"تاریخ تولید: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    
    # خط جداکننده
    c.line(50, height-70, width-50, height-70)
    
    # --- محاسبات کل ---
    y_position = height-100
    c.setFont("Helvetica-Bold", 12)
    
    daily_total = sum(inv["total"] for inv in invoices)
    service_total = sum(inv["service_fee"] for inv in invoices)
    discount_total = sum(inv["discount"] for inv in invoices)
    
    c.drawString(50, y_position, f"تعداد فاکتورها: {len(invoices)}")
    c.drawString(300, y_position, f"جمع کل فروش: {daily_total:,} تومان")
    y_position -= 25
    
    c.drawString(50, y_position, f"مجموع حق سرویس: {service_total:,} تومان")
    c.drawString(300, y_position, f"مجموع تخفیف‌ها: {discount_total:,} تومان")
    y_position -= 40
    
    # --- جدول فاکتورها ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "خلاصه فاکتورها:")
    y_position -= 20
    
    # داده‌های جدول
    data = [["شماره", "ساعت", "تعداد آیتم‌ها", "جمع جزء", "سرویس", "تخفیف", "جمع نهایی"]]
    
    for inv in invoices:
        subtotal = sum(item["price"]*item["quantity"] for item in inv["items"])
        data.append([
            str(inv["id"]),
            inv["date"][11:16],
            str(len(inv["items"])),
            f"{subtotal:,}",
            f"{inv['service_fee']:,}",
            f"{inv['discount']:,}",
            f"{inv['total']:,}"
        ])
    
    # طراحی جدول
    table = Table(data, colWidths=[40, 40, 60, 80, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ]))
    
    table.wrapOn(c, width-100, height)
    table.drawOn(c, 50, y_position-20-len(invoices)*20)
    
    # --- جزئیات آیتم‌ها ---
    y_position -= len(invoices)*20 + 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "جزئیات آیتم‌های فروش:")
    y_position -= 30
    
    for inv in invoices:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, f"فاکتور #{inv['id']} - {inv['date'][:16]}")
        y_position -= 20
        
        c.setFont("Helvetica", 9)
        for item in inv["items"]:
            item_text = f"{item['name']} ({item['quantity']} × {item['price']:,}) = {item['price']*item['quantity']:,}"
            c.drawString(70, y_position, item_text)
            y_position -= 15
        
        y_position -= 10
    
    # پاورقی
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 30, "این گزارش به صورت خودکار توسط سیستم صندوق رستوران تولید شده است")
    
    c.save()