from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView, QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt
from database.models import MENU

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم سفارش رستوران - نسخه حرفه‌ای")
        self.setup_ui()
        self.current_order = []

    def setup_ui(self):
        # لایه اصلی
        main_layout = QHBoxLayout()

        # بخش دسته‌بندی‌ها (تب‌های عمودی)
        self.categories_tabs = QTabWidget()
        self.categories_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.setup_menu_tabs()

        # بخش سفارش و محاسبات
        order_section = QVBoxLayout()

        # جدول سفارشات
        self.order_table = QTableWidget(0, 4)
        self.order_table.setHorizontalHeaderLabels(["آیتم", "قیمت", "تعداد", "جمع"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # بخش محاسبات
        calc_layout = QVBoxLayout()

        # حق سرویس
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("حق سرویس (%):"))
        self.service_spin = QSpinBox()
        self.service_spin.setRange(0, 30)
        self.service_spin.setValue(10)
        service_layout.addWidget(self.service_spin)

        # تخفیف
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("تخفیف (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        discount_layout.addWidget(self.discount_spin)

        # جمع کل
        self.total_label = QLabel("جمع کل: 0 تومان")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        calc_layout.addLayout(service_layout)
        calc_layout.addLayout(discount_layout)
        calc_layout.addWidget(self.total_label)

        order_section.addWidget(self.order_table)
        order_section.addLayout(calc_layout)

        main_layout.addWidget(self.categories_tabs, 1)
        main_layout.addLayout(order_section, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setup_menu_tabs(self):
        """ایجاد تب‌های دسته‌بندی منو"""
        for category, items in MENU.items():
            tab = QWidget()
            layout = QVBoxLayout()

            # ایجاد دکمه‌های آیتم‌ها
            for item in items:
                btn = QPushButton(f"{item['name']}\n{item['price']:,} تومان")
                btn.setMinimumHeight(60)
                btn.clicked.connect(lambda _, i=item: self.add_to_order(i))
                layout.addWidget(btn)

            tab.setLayout(layout)
            self.categories_tabs.addTab(tab, category)

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
        """آپدیت جدول سفارشات و محاسبات"""
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
        
        # محاسبه حق سرویس
        service_percent = self.service_spin.value()
        service_fee = subtotal * service_percent / 100
        
        # محاسبه تخفیف
        discount_percent = self.discount_spin.value()
        discount = (subtotal + service_fee) * discount_percent / 100
        
        total = subtotal + service_fee - discount
        
        self.total_label.setText(
            f"جمع کل: {total:,.0f} تومان\n"
            f"(جمع جزء: {subtotal:,.0f} | "
            f"حق سرویس: {service_fee:,.0f} | "
            f"تخفیف: {discount:,.0f})"
        )