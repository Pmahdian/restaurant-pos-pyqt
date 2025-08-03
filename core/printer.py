from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.units import mm

def generate_invoice_pdf(items, filename, invoice_number, date, total):
    _generate_customer_version(items, filename, invoice_number, date, total)
    _generate_kitchen_version(items, filename, invoice_number, date)

def _generate_customer_version(items, base_filename, invoice_number, date, total):
    filename = f"customer_{base_filename}"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=10*mm, leftMargin=10*mm)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("<b>فاکتور مشتری</b>", styles['Title']))
    elements.append(Paragraph(f"<b>شماره فاکتور:</b> {invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"<b>تاریخ:</b> {date}", styles['Normal']))
    elements.append(Paragraph("_________________________________________", styles['Normal']))
    
    table_data = [
        ["ردیف", "آیتم", "تعداد", "قیمت واحد", "جمع", "توضیحات"]
    ]
    
    for idx, item in enumerate(items, 1):
        table_data.append([
            str(idx),
            item['name'],
            str(item['quantity']),
            f"{item['price']:,}",
            f"{item['price'] * item['quantity']:,}",
            item.get('description', '')
        ])
    
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    service_charge = subtotal * 0.10
    discount = 0
    grand_total = total
    
    table = Table(table_data, colWidths=[20, 80, 30, 50, 50, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(table)
    
    summary_data = [
        ["جمع جزء:", f"{subtotal:,}"],
        ["حق سرویس (10%):", f"{service_charge:,}"],
        ["تخفیف:", f"{discount:,}"],
        ["<b>جمع کل:</b>", f"<b>{grand_total:,}</b>"]
    ]
    
    summary_table = Table(summary_data, colWidths=[100, 100])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    elements.append(summary_table)
    
    elements.append(Paragraph("_________________________________________", styles['Normal']))
    elements.append(Paragraph("با تشکر از خرید شما", styles['Normal']))
    elements.append(Paragraph("تلفن: 021-12345678", styles['Normal']))
    
    doc.build(elements)

def _generate_kitchen_version(items, base_filename, invoice_number, date):
    filename = f"kitchen_{base_filename}"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=10*mm, leftMargin=10*mm)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("<b>سفارش آشپزخانه</b>", styles['Title']))
    elements.append(Paragraph(f"<b>شماره سفارش:</b> {invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"<b>زمان:</b> {date.split()[1]}", styles['Normal']))
    elements.append(Paragraph("_________________________________________", styles['Normal']))
    
    table_data = [
        ["ردیف", "آیتم", "تعداد", "توضیحات"]
    ]
    
    for idx, item in enumerate(items, 1):
        table_data.append([
            str(idx),
            item['name'],
            str(item['quantity']),
            item.get('description', '')
        ])
    
    table = Table(table_data, colWidths=[20, 100, 30, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(table)
    
    elements.append(Paragraph("_________________________________________", styles['Normal']))
    elements.append(Paragraph("<b>زمان تحویل: ______</b>", styles['Normal']))
    elements.append(Paragraph("لطفا به نکات درج شده توجه فرمایید", styles['Normal']))
    
    doc.build(elements)