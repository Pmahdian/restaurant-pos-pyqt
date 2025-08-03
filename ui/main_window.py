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
from pathlib import Path

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
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # دکمه سفارش جدید
        new_order_btn = QPushButton("سفارش جدید")
        new_order_btn.clicked.connect(self.reset_order)
        toolbar.addWidget(new_order_btn)
        
        # دکمه گزارش فروش
        report_btn = QPushButton("گزارش فروش")
        report_btn.clicked.connect(self.show_daily_sales)
        toolbar.addWidget(report_btn)

        # صفحه اصلی
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # اطلاعات فاکتور
        self.invoice_label = QLabel(f"فاکتور # {self.invoice_counter}")
        self.invoice_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.invoice_label)
        
        # بخش منو و سفارش
        order_layout = QHBoxLayout()
        
        # تب‌های منو
        self.categories_tabs = QTabWidget()
        self.categories_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.setup_menu_tabs()
        order_layout.addWidget(self.categories_tabs, 1)
        
        # جدول سفارش
        right_section = QVBoxLayout()
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
        self.total_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        
        # دکمه‌های اقدام
        btn_layout = QHBoxLayout()
        print_btn = QPushButton("چاپ فاکتور")
        print_btn.setStyleSheet("background-color: #3498db; color: white;")
        print_btn.clicked.connect(self.print_invoice)
        
        btn_layout.addWidget(print_btn)
        
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
        """پاک کردن سفارش جاری و شروع جدید"""
        self.current_order = []
        self.order_table.setRowCount(0)
        self.total_label.setText("جمع کل: 0 تومان")
        self.service_spin.setValue(10)
        self.discount_spin.setValue(0)

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
        """به‌روزرسانی جدول سفارش"""
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
        """محاسبه جمع کل"""
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
        """چاپ فاکتور و ذخیره"""
        if not self.current_order:
            QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
            return
            
        try:
            total, service_fee, discount = self.calculate_total()
            
            # ذخیره در لیست موقت
            invoice_id = len(self.temp_invoices) + 1
            self.temp_invoices.append({
                "id": invoice_id,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": self.current_order.copy(),
                "total": total,
                "service_fee": service_fee,
                "discount": discount
            })
            
            # چاپ فاکتور
            self.print_to_pos_printer(total)
            
            # ریست برای سفارش جدید
            self.reset_order()
            self.invoice_counter += 1
            self.invoice_label.setText(f"فاکتور # {self.invoice_counter}")
            
            QMessageBox.information(self, "موفق", "فاکتور با موفقیت چاپ شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ فاکتور:\n{str(e)}")

    def print_to_pos_printer(self, total):
        """چاپ به پرینتر فیش (نمونه کد)"""
        # اینجا کد مخصوص چاپگر خود را قرار دهید
        print("------ فاکتور فروش ------")
        print(f"شماره: {self.invoice_counter}")
        print(f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        print("------------------------")
        for item in self.current_order:
            print(f"{item['name']} {item['quantity']} x {item['price']:,}")
        print("------------------------")
        print(f"جمع کل: {total:,} تومان")
        print("------ با تشکر ------")
        
        # اگر چاپگر جواب نداد، نسخه PDF ایجاد شود
        self.generate_backup_pdf()

    def generate_backup_pdf(self):
        """ایجاد نسخه پشتیبان PDF"""
        try:
            os.makedirs("فاکتورها", exist_ok=True)
            filename = f"فاکتورها/فاکتور_{self.invoice_counter}.pdf"
            from core.printer import generate_invoice_pdf
            generate_invoice_pdf(self.current_order, filename, self.invoice_counter)
        except Exception as e:
            print(f"خطا در ایجاد نسخه پشتیبان: {e}")

    def show_daily_sales(self):
        """نمایش گزارش فروش"""
        if not self.temp_invoices:
            QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش وجود ندارد")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("گزارش فروش روزانه")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # جمع کل روز
        total = sum(inv["total"] for inv in self.temp_invoices)
        total_label = QLabel(f"<h3>جمع کل فروش: {total:,} تومان</h3>")
        layout.addWidget(total_label)
        
        # جدول گزارش
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["شماره فاکتور", "تاریخ", "تعداد آیتم", "جمع کل"])
        
        table.setRowCount(len(self.temp_invoices))
        for row, inv in enumerate(self.temp_invoices):
            table.setItem(row, 0, QTableWidgetItem(str(inv["id"])))
            table.setItem(row, 1, QTableWidgetItem(inv["date"]))
            table.setItem(row, 2, QTableWidgetItem(str(len(inv["items"]))))
            table.setItem(row, 3, QTableWidgetItem(f"{inv['total']:,}"))
        
        layout.addWidget(table)
        
        # دکمه ذخیره
        save_btn = QPushButton("ذخیره گزارش")
        save_btn.clicked.connect(lambda: self.save_daily_report(dialog))
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec()

    def save_daily_report(self, dialog):
        """ذخیره گزارش روزانه"""
        try:
            os.makedirs("گزارشات", exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"گزارشات/گزارش_{date_str}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.temp_invoices, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(dialog, "موفق", f"گزارش در {filename} ذخیره شد")
            dialog.close()
        except Exception as e:
            QMessageBox.critical(dialog, "خطا", f"خطا در ذخیره گزارش:\n{str(e)}")