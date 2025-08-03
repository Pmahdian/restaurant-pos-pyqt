from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView, QSpinBox, QMessageBox,
    QToolBar, QDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime
from core.printer import generate_invoice_pdf
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم فروش رستوران - نسخه موقت")
        self.current_order = []
        self.temp_invoices = []  # ذخیره موقت فاکتورها
        self.setup_ui()

    def setup_ui(self):
        # نوار ابزار
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # دکمه فروش روزانه
        daily_sales_btn = QPushButton("گزارش فروش روزانه")
        daily_sales_btn.clicked.connect(self.show_daily_sales)
        toolbar.addWidget(daily_sales_btn)

        # دکمه حذف همه
        clear_btn = QPushButton("حذف همه داده‌ها")
        clear_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        clear_btn.clicked.connect(self.clear_all_data)
        toolbar.addWidget(clear_btn)

        # بقیه رابط کاربری مثل قبل...
        # [کدهای قبلی رابط کاربری بدون تغییر می‌ماند]

    def save_invoice_action(self, total, service_fee, discount):
        """ذخیره موقت فاکتور"""
        invoice = {
            "id": len(self.temp_invoices) + 1,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "items": self.current_order.copy(),
            "total": total,
            "service_fee": service_fee,
            "discount": discount
        }
        self.temp_invoices.append(invoice)
        return invoice["id"]

    def show_daily_sales(self):
        """نمایش گزارش فروش روزانه"""
        if not self.temp_invoices:
            QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش وجود ندارد")
            return

        # ایجاد پنجره گزارش
        report_dialog = QDialog(self)
        report_dialog.setWindowTitle("گزارش فروش روزانه")
        report_dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # جدول گزارش
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["شماره فاکتور", "تاریخ", "تعداد آیتم", "جمع کل", "جزئیات"])

        # محاسبه جمع کل روز
        daily_total = sum(inv["total"] for inv in self.temp_invoices)

        # پر کردن جدول
        table.setRowCount(len(self.temp_invoices))
        for row, invoice in enumerate(self.temp_invoices):
            table.setItem(row, 0, QTableWidgetItem(str(invoice["id"])))
            table.setItem(row, 1, QTableWidgetItem(invoice["date"]))
            table.setItem(row, 2, QTableWidgetItem(str(len(invoice["items"]))))
            table.setItem(row, 3, QTableWidgetItem(f"{invoice['total']:,} تومان"))

            # دکمه جزئیات
            details_btn = QPushButton("مشاهده")
            details_btn.clicked.connect(lambda _, inv=invoice: self.show_invoice_details(inv))
            table.setCellWidget(row, 4, details_btn)

        # دکمه‌های اقدام
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("ذخیره دائمی گزارش")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        save_btn.clicked.connect(self.save_permanent)
        
        print_btn = QPushButton("چاپ گزارش")
        print_btn.setStyleSheet("background-color: #3498db; color: white;")
        print_btn.clicked.connect(self.print_report)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(print_btn)

        # نمایش جمع کل
        total_label = QLabel(f"<h3>جمع کل فروش روز: {daily_total:,} تومان</h3>")
        
        layout.addWidget(total_label)
        layout.addWidget(table)
        layout.addLayout(btn_layout)
        
        report_dialog.setLayout(layout)
        report_dialog.exec()

    def show_invoice_details(self, invoice):
        """نمایش جزئیات فاکتور"""
        details = "جزئیات فاکتور:\n\n"
        for item in invoice["items"]:
            details += f"{item['name']} - {item['quantity']} x {item['price']:,} = {item['price'] * item['quantity']:,}\n"
        
        details += f"\nحق سرویس: {invoice['service_fee']:,}\n"
        details += f"تخفیف: {invoice['discount']:,}\n"
        details += f"جمع کل: {invoice['total']:,}"
        
        QMessageBox.information(self, f"فاکتور #{invoice['id']}", details)

    def save_permanent(self):
        """ذخیره دائمی در فایل JSON"""
        try:
            with open("daily_sales.json", "w", encoding="utf-8") as f:
                json.dump(self.temp_invoices, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "موفق", "گزارش با موفقیت ذخیره شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره گزارش: {str(e)}")

    def print_report(self):
        """چاپ گزارش به صورت PDF"""
        try:
            filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.pdf"
            generate_invoice_pdf(self.temp_invoices, filename)
            QMessageBox.information(self, "موفق", f"گزارش در فایل {filename} ذخیره شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش: {str(e)}")

    def clear_all_data(self):
        """حذف تمام داده‌ها"""
        reply = QMessageBox.question(
            self,
            "تایید حذف",
            "آیا مطمئنید می‌خواهید تمام داده‌ها را حذف کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.temp_invoices = []
            self.current_order = []
            self.order_table.setRowCount(0)
            self.total_label.setText("جمع کل: 0 تومان")
            QMessageBox.information(self, "موفق", "تمام داده‌ها حذف شدند")