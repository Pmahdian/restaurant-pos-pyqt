from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView, QSpinBox, QMessageBox,
    QToolBar, QDialog, QStackedWidget  # <-- اینجا اضافه شد
)
from PyQt6.QtCore import Qt
from datetime import datetime
from core.printer import generate_invoice_pdf
import json
import os
from openpyxl import Workbook
from pathlib import Path
import platform
from PyQt6.QtWidgets import QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم فروش رستوران")
        self.current_order = []
        self.temp_invoices = []
        self.invoice_counter = 1
        self.setup_ui()
 

    def get_desktop_path():
        """پیدا کردن مسیر دسکتاپ برای سیستم‌عامل‌های مختلف"""
        home = Path.home()
        if platform.system() == "Windows":
            return home / "Desktop"
        elif platform.system() == "Darwin":  # macOS
            return home / "Desktop"
        else:  # Linux/دیگر سیستم‌ها
            return home / "Desktop"

    def setup_ui(self):
        # ویجت پشته‌ای برای تغییر صفحات
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # صفحه سفارش‌گیری (اصلی)
        self.order_page = self.create_order_page()
        self.stacked_widget.addWidget(self.order_page)
        
        # صفحه گزارش فروش
        self.report_page = self.create_report_page()
        self.stacked_widget.addWidget(self.report_page)
        
        # نوار ابزار برای دکمه‌های اصلی
        toolbar = QToolBar("ابزارهای اصلی")
        self.addToolBar(toolbar)
        
        # دکمه‌های نوار ابزار
        order_btn = QPushButton("سفارش جدید")
        order_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        toolbar.addWidget(order_btn)
        
        report_btn = QPushButton("گزارش فروش روزانه")
        report_btn.clicked.connect(self.show_daily_sales)
        toolbar.addWidget(report_btn)
        
        clear_btn = QPushButton("حذف همه داده‌ها")
        clear_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        clear_btn.clicked.connect(self.clear_all_data)
        toolbar.addWidget(clear_btn)

    def create_order_page(self):
        """ایجاد صفحه سفارش‌گیری"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # اطلاعات فاکتور
        self.invoice_label = QLabel(f"فاکتور # {self.invoice_counter} | تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        self.invoice_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.invoice_label)
        
        # بخش اصلی سفارش
        order_layout = QHBoxLayout()
        
        # تب‌های دسته‌بندی
        self.categories_tabs = QTabWidget()
        self.categories_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.setup_menu_tabs()
        order_layout.addWidget(self.categories_tabs, 1)
        
        # بخش راست (جدول سفارش و محاسبات)
        right_section = QVBoxLayout()
        
        # جدول سفارش
        self.order_table = QTableWidget(0, 4)
        self.order_table.setHorizontalHeaderLabels(["آیتم", "قیمت", "تعداد", "حذف"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_section.addWidget(self.order_table)
        
        # بخش محاسبات
        calc_layout = QVBoxLayout()
        
        # حق سرویس
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("حق سرویس (%):"))
        self.service_spin = QSpinBox()
        self.service_spin.setRange(0, 30)
        self.service_spin.setValue(10)
        self.service_spin.valueChanged.connect(self.calculate_total)
        service_layout.addWidget(self.service_spin)
        
        # تخفیف
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("تخفیف (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.valueChanged.connect(self.calculate_total)
        discount_layout.addWidget(self.discount_spin)
        
        # جمع کل
        self.total_label = QLabel("جمع کل: 0 تومان")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #27ae60;")
        
        # دکمه‌های اقدام
        btn_layout = QHBoxLayout()
        self.print_btn = QPushButton("چاپ و ذخیره فاکتور")
        self.print_btn.setStyleSheet("background-color: #3498db; color: white;")
        self.print_btn.clicked.connect(self.print_invoice)
        
        self.save_btn = QPushButton("ذخیره بدون چاپ")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        self.save_btn.clicked.connect(self.save_invoice)
        
        btn_layout.addWidget(self.print_btn)
        btn_layout.addWidget(self.save_btn)
        
        calc_layout.addLayout(service_layout)
        calc_layout.addLayout(discount_layout)
        calc_layout.addWidget(self.total_label)
        calc_layout.addLayout(btn_layout)
        
        right_section.addLayout(calc_layout)
        order_layout.addLayout(right_section, 2)
        layout.addLayout(order_layout)
        page.setLayout(layout)
        return page

    def create_report_page(self):
        """ایجاد صفحه گزارش فروش (خالی)"""
        return QWidget()

    def setup_menu_tabs(self):
        """ایجاد تب‌های دسته‌بندی منو"""
        from database.models import MENU
        
        for category, items in MENU.items():
            tab = QWidget()
            layout = QVBoxLayout()
            
            for item in items:
                btn = QPushButton(f"{item['name']}\n{item['price']:,} تومان")
                btn.setMinimumHeight(60)
                btn.clicked.connect(lambda _, item=item: self.add_to_order(item))
                layout.addWidget(btn)
            
            tab.setLayout(layout)
            self.categories_tabs.addTab(tab, category)

    def add_to_order(self, item):
        """اضافه کردن آیتم به سفارش"""
        existing = next((i for i in self.current_order if i["id"] == item["id"]), None)
        if existing:
            existing["quantity"] += 1
        else:
            self.current_order.append({
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": 1
            })
        self.update_order_table()

    def update_order_table(self):
        """به‌روزرسانی جدول سفارشات"""
        self.order_table.setRowCount(len(self.current_order))
        for row, item in enumerate(self.current_order):
            self.order_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.order_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:,}"))
            self.order_table.setItem(row, 2, QTableWidgetItem(str(item["quantity"])))
            
            # دکمه حذف
            remove_btn = QPushButton("حذف")
            remove_btn.clicked.connect(lambda _, r=row: self.remove_item(r))
            self.order_table.setCellWidget(row, 3, remove_btn)
        
        self.calculate_total()

    def remove_item(self, row):
        """حذف آیتم از سفارش"""
        if 0 <= row < len(self.current_order):
            self.current_order.pop(row)
            self.update_order_table()

    def calculate_total(self):
        """محاسبه جمع کل با اعمال حق سرویس و تخفیف"""
        subtotal = sum(item["price"] * item["quantity"] for item in self.current_order)
        service_fee = subtotal * self.service_spin.value() / 100
        discount = (subtotal + service_fee) * self.discount_spin.value() / 100
        total = subtotal + service_fee - discount
        
        self.total_label.setText(
            f"جمع کل: {total:,.0f} تومان\n"
            f"(جزء: {subtotal:,.0f} | "
            f"سرویس: {service_fee:,.0f} | "
            f"تخفیف: {discount:,.0f})"
        )
        return total, service_fee, discount

    def print_invoice(self):
        """چاپ فوری فاکتور و آماده‌سازی برای سفارش بعدی"""
        try:
            if not self.current_order:
                QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
                return

            # محاسبه جمع کل
            total, service_fee, discount = self.calculate_total()
            
            # چاپ فوری به پرینتر (اولویت اصلی)
            self.print_to_pos_printer()  # این متد را اضافه می‌کنیم
            
            # ذخیره در حافظه برای گزارش روزانه
            self.save_invoice_action(total, service_fee, discount)
            
            # آماده‌سازی برای سفارش بعدی
            self.reset_after_save()
            
            QMessageBox.information(self, "موفق", "فاکتور چاپ شد و سیستم آماده سفارش جدید است")
            
        except Exception as e:
            QMessageBox.critical(self, "خطای چاپ", f"خطا در چاپ فاکتور:\n{str(e)}")

    def print_to_pos_printer(self):
        """چاپ مستقیم به پرینتر فیش (POS)"""
        try:
            # اینجا کد مخصوص چاپگر خود را قرار دهید
            # مثال برای چاپگرهای ESC/POS:
            from escpos.printer import Usb
            printer = Usb(0x04b8, 0x0202)
            printer.text("------ فاکتور فروش ------\n")
            printer.text(f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n")
            for item in self.current_order:
                printer.text(f"{item['name']} {item['quantity']} x {item['price']:,}\n")
            printer.text("------------------------\n")
            printer.cut()
            
        except ImportError:
            # اگر کتابخانه چاپگر نصب نبود، به صورت خودکار PDF ایجاد شود
            self.generate_backup_pdf()

    def save_invoice(self):
        """ذخیره فاکتور بدون چاپ"""
        if not self.current_order:
            QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
            return
            
        total, service_fee, discount = self.calculate_total()
        self.save_invoice_action(total, service_fee, discount)
        self.reset_after_save()

    def save_invoice_action(self, total, service_fee, discount):
        """ذخیره موقت فاکتور"""
        invoice = {
            "id": len(self.temp_invoices) + 1,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.current_order.copy(),
            "total": total,
            "service_fee": service_fee,
            "discount": discount
        }
        self.temp_invoices.append(invoice)
        return invoice["id"]

    def reset_after_save(self):
        """بازنشانی پس از ذخیره"""
        self.current_order = []
        self.order_table.setRowCount(0)
        self.invoice_counter += 1
        self.invoice_label.setText(
            f"فاکتور # {self.invoice_counter} | تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        )
        self.discount_spin.setValue(0)

    def show_daily_sales(self):
        """نمایش گزارش فروش روزانه"""
        if not self.temp_invoices:
            QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش وجود ندارد")
            return
        
        # ایجاد پنجره گزارش
        report_dialog = QDialog(self)
        report_dialog.setWindowTitle("گزارش فروش روزانه")
        report_dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        
        # محاسبه جمع کل روز
        daily_total = sum(inv["total"] for inv in self.temp_invoices)
        total_label = QLabel(f"<h2>جمع کل فروش روز: {daily_total:,} تومان</h2>")
        layout.addWidget(total_label)
        
        # جدول گزارش
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["شماره", "تاریخ", "آیتم‌ها", "جمع جزء", "سرویس", "تخفیف", "جمع کل"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # پر کردن جدول
        table.setRowCount(len(self.temp_invoices))
        for row, invoice in enumerate(self.temp_invoices):
            table.setItem(row, 0, QTableWidgetItem(str(invoice["id"])))
            table.setItem(row, 1, QTableWidgetItem(invoice["date"]))
            
            # لیست آیتم‌ها
            items_text = "\n".join(
                f"{item['name']} ({item['quantity']} x {item['price']:,})" 
                for item in invoice["items"]
            )
            table.setItem(row, 2, QTableWidgetItem(items_text))
            
            # محاسبات
            subtotal = sum(item["price"] * item["quantity"] for item in invoice["items"])
            table.setItem(row, 3, QTableWidgetItem(f"{subtotal:,}"))
            table.setItem(row, 4, QTableWidgetItem(f"{invoice['service_fee']:,}"))
            table.setItem(row, 5, QTableWidgetItem(f"{invoice['discount']:,}"))
            table.setItem(row, 6, QTableWidgetItem(f"{invoice['total']:,}"))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        # دکمه‌های اقدام
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("ذخیره دائمی گزارش")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        save_btn.clicked.connect(self.save_permanent)
        
        print_btn = QPushButton("چاپ گزارش")
        print_btn.setStyleSheet("background-color: #3498db; color: white;")
        print_btn.clicked.connect(self.print_report)
        
        close_btn = QPushButton("بستن")
        close_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        close_btn.clicked.connect(report_dialog.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        report_dialog.setLayout(layout)
        report_dialog.exec()

    def save_permanent(self):
        """ذخیره دائمی گزارش در پوشه فروش کل روی دسکتاپ"""
        try:
            # ایجاد پوشه فروش کل اگر وجود نداشته باشد
            desktop = Path(get_desktop_path())
            sales_folder = desktop / "فروش کل"
            sales_folder.mkdir(exist_ok=True, parents=True)
            
            # نام فایل براساس تاریخ
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # ذخیره PDF
            pdf_path = sales_folder / f"فروش_{date_str}.pdf"
            from core.printer import generate_invoice_pdf
            generate_invoice_pdf(self.temp_invoices, str(pdf_path))
            
            # ذخیره Excel
            excel_path = sales_folder / f"فروش_{date_str}.xlsx"
            self.save_to_excel(str(excel_path))
            
            QMessageBox.information(
                self, 
                "ذخیره گزارش", 
                f"گزارش با موفقیت ذخیره شد در:\n{str(sales_folder)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره گزارش:\n{str(e)}")

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
            self.invoice_counter = 1
            self.invoice_label.setText(
                f"فاکتور # {self.invoice_counter} | تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}"
            )
            QMessageBox.information(self, "موفق", "تمام داده‌ها حذف شدند")


    def get_desktop_path():
        """پیدا کردن مسیر دسکتاپ براساس سیستم عامل"""
        home = Path.home()
        if platform.system() == "Windows":
            return home / "Desktop"
        elif platform.system() == "Darwin":  # macOS
            return home / "Desktop"
        else:  # Linux
            return home / "Desktop"
        

    def save_to_excel(self, file_path):
        """ذخیره گزارش در فایل اکسل"""
        wb = Workbook()
        ws = wb.active
        ws.title = "گزارش فروش"
        
        # هدرهای جدول
        headers = [
            "شماره فاکتور", "تاریخ", "آیتم‌ها", 
            "تعداد", "قیمت واحد", "جمع جزء", 
            "حق سرویس", "تخفیف", "جمع کل"
        ]
        ws.append(headers)
        
        # اضافه کردن داده‌ها
        for inv in self.temp_invoices:
            for item in inv["items"]:
                row = [
                    inv["id"],
                    inv["date"],
                    item["name"],
                    item["quantity"],
                    item["price"],
                    item["price"] * item["quantity"],
                    inv["service_fee"],
                    inv["discount"],
                    inv["total"]
                ]
                ws.append(row)
        
        # ذخیره فایل
        wb.save(file_path)

    def generate_backup_pdf(self):
        """ایجاد نسخه پشتیبان PDF در پوشه پروژه"""
        try:
            # ساخت پوشه اگر وجود نداشته باشد
            os.makedirs("فاکتورهای روزانه", exist_ok=True)
            
            # نام فایل بر اساس تاریخ و ساعت
            filename = f"فاکتورهای روزانه/فاکتور_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # تولید PDF
            from core.printer import generate_invoice_pdf
            generate_invoice_pdf([{
                "id": len(self.temp_invoices) + 1,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": self.current_order,
                "total": self.calculate_total()[0],
                "service_fee": self.service_spin.value(),
                "discount": self.discount_spin.value()
            }], filename)
            
        except Exception as e:
            print(f"خطا در ایجاد نسخه پشتیبان: {e}")