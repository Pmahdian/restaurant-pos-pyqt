from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from database.models import MENU, save_invoice_to_db
from datetime import datetime
import os

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # تعریف تمام متغیرهای کلاس
        self.current_order = []
        self.invoice_counter = 1
        self.categories_tabs = None
        self.order_table = None
        self.service_spin = None
        self.discount_spin = None
        self.total_label = None
        self.print_btn = None
        self.save_btn = None
        self.invoice_label = None
        
        self.setWindowTitle("سیستم سفارش رستوران - نسخه نهایی")
        self.setup_ui()
      


    def setup_menu_tabs(self):
        """ایجاد تب‌های دسته‌بندی منو"""
        for category, items in MENU.items():
            tab = QWidget()
            layout = QVBoxLayout()

            # ایجاد دکمه‌های آیتم‌ها
            for item in items:
                btn = QPushButton(f"{item['name']}\n{item['price']:,} تومان")
                btn.setMinimumHeight(60)
                btn.clicked.connect(lambda _, item=item: self.add_to_order(item))
                layout.addWidget(btn)

            tab.setLayout(layout)
            self.categories_tabs.addTab(tab, category)

    

    def setup_ui(self):
        main_layout = QHBoxLayout()
        
        # --- بخش منو ---
        self.categories_tabs = QTabWidget()
        self.categories_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.setup_menu_tabs()
        
        # --- بخش سفارش ---
        order_section = QVBoxLayout()
        
        # اطلاعات فاکتور
        self.invoice_label = QLabel(f"فاکتور # {self.invoice_counter} | تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
        self.invoice_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        # جدول سفارش
        self.order_table = QTableWidget(0, 4)
        self.order_table.setHorizontalHeaderLabels(["آیتم", "قیمت", "تعداد", "حذف"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # بخش محاسبات
        calc_layout = QVBoxLayout()
        
        # حق سرویس
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("حق سرویس (%):"))
        self.service_spin = QSpinBox()
        self.service_spin.setRange(0, 30)
        self.service_spin.setValue(10)
        self.service_spin.valueChanged.connect(self.calculate_total)  # تغییر خودکار
        service_layout.addWidget(self.service_spin)
        
        # تخفیف
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("تخفیف (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.valueChanged.connect(self.calculate_total)  # تغییر خودکار
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
        
        order_section.addWidget(self.invoice_label)
        order_section.addWidget(self.order_table)
        order_section.addLayout(calc_layout)
        
        main_layout.addWidget(self.categories_tabs, 1)
        main_layout.addLayout(order_section, 2)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # ... (متدهای setup_menu_tabs, add_to_order, remove_item مثل قبل)

    def calculate_total(self):
        """محاسبه خودکار با تغییر درصدها"""
        subtotal = sum(item["price"] * item["quantity"] for item in self.current_order)
        service_fee = subtotal * self.service_spin.value() / 100
        discount = (subtotal + service_fee) * self.discount_spin.value() / 100
        total = subtotal + service_fee - discount
        
        self.total_label.setText(
            f"جمع کل: {total:,.0f} تومان\n"
            f"(جزء: {subtotal:,.0f} | "
            f"حق سرویس: {service_fee:,.0f} | "
            f"تخفیف: {discount:,.0f})"
        )
        return total, service_fee, discount

    def print_invoice(self):
        """چاپ فاکتور + ذخیره"""
        if not self.current_order:
            QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
            return
            
        total, service_fee, discount = self.calculate_total()
        self.save_invoice_action(total, service_fee, discount)
        
        # TODO: اضافه کردن کد چاپ واقعی اینجا
        QMessageBox.information(self, "چاپ فاکتور", "فاکتور با موفقیت چاپ و ذخیره شد.")
        self.reset_after_save()

    def save_invoice(self):
        """ذخیره بدون چاپ"""
        if not self.current_order:
            QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
            return
            
        total, service_fee, discount = self.calculate_total()
        self.save_invoice_action(total, service_fee, discount)
        self.reset_after_save()

    def save_invoice_action(self, total, service_fee, discount):
        """ذخیره فاکتور در دیتابیس"""
        invoice_id = save_invoice_to_db(
            self.current_order,
            total,
            service_fee,
            discount
        )
        return invoice_id

    def reset_after_save(self):
        """ریست فرم پس از ذخیره"""
        self.current_order = []
        self.order_table.setRowCount(0)
        self.invoice_counter += 1
        self.invoice_label.setText(
            f"فاکتور # {self.invoice_counter} | تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        )
        self.discount_spin.setValue(0)

    def add_to_order(self, item):
        """اضافه کردن آیتم به سفارش"""
        # بررسی وجود آیتم در سفارش
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
        """آپدیت جدول سفارشات"""
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