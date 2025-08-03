from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView, QSpinBox, QMessageBox,
    QToolBar, QDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime
from core.printer import generate_invoice_pdf
import os
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم فروش رستوران")
        self.current_order = []
        self.temp_invoices = []
        self.invoice_counter = 1
        self.setup_ui()

    def setup_ui(self):
        # نوار ابزار
        toolbar = QToolBar("ابزارهای اصلی")
        self.addToolBar(toolbar)

        # دکمه‌های نوار ابزار
        self.new_order_btn = QPushButton("سفارش جدید")
        self.new_order_btn.clicked.connect(self.reset_order)
        toolbar.addWidget(self.new_order_btn)

        self.report_btn = QPushButton("گزارش فروش")
        self.report_btn.clicked.connect(self.show_daily_sales)
        toolbar.addWidget(self.report_btn)

        # صفحه اصلی
        main_widget = QWidget()
        layout = QVBoxLayout()

        # اطلاعات فاکتور
        self.invoice_label = QLabel(f"فاکتور # {self.invoice_counter}")
        self.invoice_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        layout.addWidget(self.invoice_label)

        # بخش منو و سفارش
        order_layout = QHBoxLayout()

        # تب‌های منو
        self.categories_tabs = QTabWidget()
        self.categories_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.setup_menu_tabs()
        order_layout.addWidget(self.categories_tabs, 1)

        # بخش سفارشات
        right_section = QVBoxLayout()

        # جدول سفارشات
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
        
        self.save_btn = QPushButton("ذخیره فاکتور")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        self.save_btn.clicked.connect(self.save_invoice)
        
        self.print_btn = QPushButton("چاپ و ذخیره")
        self.print_btn.setStyleSheet("background-color: #3498db; color: white;")
        self.print_btn.clicked.connect(self.print_invoice)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.print_btn)

        calc_layout.addLayout(service_layout)
        calc_layout.addLayout(discount_layout)
        calc_layout.addWidget(self.total_label)
        calc_layout.addLayout(btn_layout)

        right_section.addLayout(calc_layout)
        order_layout.addLayout(right_section, 2)
        layout.addLayout(order_layout)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def reset_order(self):
        """بازنشانی سفارش جاری"""
        self.current_order = []
        self.order_table.setRowCount(0)
        self.total_label.setText("جمع کل: 0 تومان")
        self.service_spin.setValue(10)
        self.discount_spin.setValue(0)
        self.invoice_counter += 1
        self.invoice_label.setText(f"فاکتور # {self.invoice_counter}")

    def setup_menu_tabs(self):
        """ایجاد تب‌های منو"""
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
        """اضافه کردن آیتم به سفارش جاری"""
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
            remove_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            remove_btn.clicked.connect(lambda _, r=row: self.remove_item(r))
            self.order_table.setCellWidget(row, 3, remove_btn)
        
        self.calculate_total()

    def remove_item(self, row):
        """حذف آیتم از سفارش جاری"""
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

    def save_invoice(self):
        """ذخیره فاکتور بدون چاپ"""
        if not self.current_order:
            QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
            return
            
        try:
            total, service_fee, discount = self.calculate_total()
            self.save_invoice_action(total, service_fee, discount)
            QMessageBox.information(self, "موفق", "فاکتور با موفقیت ذخیره شد")
            self.reset_order()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره فاکتور:\n{str(e)}")

    def print_invoice(self):
        """چاپ فاکتور بعد از ذخیره اجباری"""
        if not self.current_order:
            QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
            return
            
        try:
            # ذخیره اجباری اول
            total, service_fee, discount = self.calculate_total()
            invoice_id = self.save_invoice_action(total, service_fee, discount)
            
            # چاپ فاکتور
            self.print_to_pos_printer(total)
            
            # نمایش پیام و ریست
            QMessageBox.information(self, "موفق", "فاکتور چاپ و ذخیره شد")
            self.reset_order()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ فاکتور:\n{str(e)}")

    def save_invoice_action(self, total, service_fee, discount):
        """ذخیره فاکتور در لیست موقت"""
        invoice = {
            "id": self.invoice_counter,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.current_order.copy(),
            "total": total,
            "service_fee": service_fee,
            "discount": discount
        }
        self.temp_invoices.append(invoice)
        return invoice["id"]

    def print_to_pos_printer(self, total):
        """چاپ فاکتور به پرینتر (نسخه شبیه‌سازی شده)"""
        try:
            # چاپ به پرینتر فیزیکی
            print("\n\n------ چاپ به پرینتر ------")
            print(f"فاکتور # {self.invoice_counter}")
            print(f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
            print("--------------------------")
            for item in self.current_order:
                print(f"{item['name']} {item['quantity']} × {item['price']:,}")
            print("--------------------------")
            print(f"جمع کل: {total:,} تومان")
            print("------ با تشکر ------")
            print("\n\n")
            
            # ایجاد نسخه PDF پشتیبان
            self.generate_backup_pdf()
        except Exception as e:
            raise Exception(f"خطا در چاپگر: {str(e)}")

    def generate_backup_pdf(self):
        """ایجاد نسخه PDF پشتیبان"""
        try:
            os.makedirs("فاکتورهای_چاپی", exist_ok=True)
            filename = f"فاکتورهای_چاپی/فاکتور_{self.invoice_counter}.pdf"
            from core.printer import generate_invoice_pdf
            generate_invoice_pdf(
                self.current_order,
                filename,
                self.invoice_counter,
                datetime.now().strftime("%Y/%m/%d %H:%M"),
                self.calculate_total()[0]
            )
        except Exception as e:
            print(f"خطا در ایجاد نسخه PDF: {str(e)}")

    def show_daily_sales(self):
        """نمایش گزارش فروش روزانه با امکان چاپ مجدد"""
        if not self.temp_invoices:
            QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش وجود ندارد")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("گزارش فروش روزانه")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # جمع کل روز
        daily_total = sum(inv["total"] for inv in self.temp_invoices)
        total_label = QLabel(f"<h2>جمع کل فروش روز: {daily_total:,} تومان</h2>")
        layout.addWidget(total_label)

        # جدول گزارش
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["شماره", "تاریخ", "تعداد آیتم", "جمع کل", "جزئیات", "چاپ مجدد"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # پر کردن جدول
        table.setRowCount(len(self.temp_invoices))
        for row, inv in enumerate(self.temp_invoices):
            table.setItem(row, 0, QTableWidgetItem(str(inv["id"])))
            table.setItem(row, 1, QTableWidgetItem(inv["date"]))
            table.setItem(row, 2, QTableWidgetItem(str(len(inv["items"]))))
            table.setItem(row, 3, QTableWidgetItem(f"{inv['total']:,}"))

            # دکمه جزئیات
            details_btn = QPushButton("مشاهده")
            details_btn.setStyleSheet("background-color: #f39c12; color: white;")
            details_btn.clicked.connect(lambda _, inv=inv: self.show_invoice_details(inv))
            table.setCellWidget(row, 4, details_btn)

            # دکمه چاپ مجدد
            reprint_btn = QPushButton("چاپ مجدد")
            reprint_btn.setStyleSheet("background-color: #3498db; color: white;")
            reprint_btn.clicked.connect(lambda _, inv=inv: self.reprint_invoice(inv))
            table.setCellWidget(row, 5, reprint_btn)

        table.resizeColumnsToContents()
        layout.addWidget(table)

        # دکمه ذخیره گزارش
        save_btn = QPushButton("ذخیره گزارش کامل")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        save_btn.clicked.connect(self.save_full_report)
        layout.addWidget(save_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def show_invoice_details(self, invoice):
        """نمایش جزئیات فاکتور"""
        details = "جزئیات فاکتور:\n\n"
        details += f"شماره فاکتور: {invoice['id']}\n"
        details += f"تاریخ: {invoice['date']}\n"
        details += "------------------------\n"
        
        for item in invoice["items"]:
            details += f"{item['name']} {item['quantity']} × {item['price']:,} = {item['price'] * item['quantity']:,}\n"
        
        details += "------------------------\n"
        details += f"جمع جزء: {sum(item['price'] * item['quantity'] for item in invoice['items']):,}\n"
        details += f"حق سرویس: {invoice['service_fee']:,}\n"
        details += f"تخفیف: {invoice['discount']:,}\n"
        details += f"جمع کل: {invoice['total']:,}"
        
        QMessageBox.information(self, f"جزئیات فاکتور #{invoice['id']}", details)

    def reprint_invoice(self, invoice):
        """چاپ مجدد فاکتور از تاریخچه"""
        try:
            self.print_to_pos_printer(invoice["total"])
            QMessageBox.information(self, "موفق", f"فاکتور #{invoice['id']} با موفقیت چاپ مجدد شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ مجدد:\n{str(e)}")

    def save_full_report(self):
        """ذخیره گزارش کامل روزانه"""
        try:
            os.makedirs("گزارشات_روزانه", exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"گزارشات_روزانه/گزارش_{date_str}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.temp_invoices, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "موفق", f"گزارش روزانه در {filename} ذخیره شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره گزارش:\n{str(e)}")


    def save_full_report(self):
        """ذخیره گزارش کامل روزانه به صورت Excel"""
        try:
            from openpyxl import Workbook
            import os
            
            # ایجاد پوشه گزارشات
            os.makedirs("گزارشات_روزانه", exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"گزارشات_روزانه/گزارش_{date_str}.xlsx"
            
            # ایجاد فایل Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "گزارش فروش"
            
            # نوشتن هدرها
            headers = [
                "شماره فاکتور", "تاریخ", "آیتم", 
                "تعداد", "قیمت واحد", "جمع جزء",
                "حق سرویس", "تخفیف", "جمع کل"
            ]
            ws.append(headers)
            
            # پر کردن داده‌ها
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
            
                # اضافه کردن یک ردیف خالی بین فاکتورها
                ws.append([])
            
            # ذخیره فایل
            wb.save(filename)
            
            QMessageBox.information(
                self, 
                "ذخیره گزارش", 
                f"گزارش با موفقیت در فایل زیر ذخیره شد:\n{filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "خطا", 
                f"خطا در ذخیره گزارش Excel:\n{str(e)}"
            )