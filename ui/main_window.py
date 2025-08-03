from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QSpinBox, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from database.models import MENU

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم سفارش رستوران")
        self.setup_ui()

    def setup_ui(self):
        # لیست سفارشات جاری
        self.order_items = []

        # ویجت‌های اصلی
        self.category_combo = QComboBox()
        self.category_combo.addItems(MENU.keys())
        self.category_combo.currentTextChanged.connect(self.update_items_combo)

        self.item_combo = QComboBox()
        self.update_items_combo()

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setValue(1)

        self.add_btn = QPushButton("اضافه به سفارش")
        self.add_btn.clicked.connect(self.add_to_order)

        # جدول سفارشات
        self.order_table = QTableWidget(0, 3)
        self.order_table.setHorizontalHeaderLabels(["آیتم", "تعداد", "قیمت"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # لایه‌بندی
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("دسته‌بندی:"))
        form_layout.addWidget(self.category_combo)
        form_layout.addWidget(QLabel("آیتم:"))
        form_layout.addWidget(self.item_combo)
        form_layout.addWidget(QLabel("تعداد:"))
        form_layout.addWidget(self.quantity_spin)
        form_layout.addWidget(self.add_btn)

        layout.addLayout(form_layout)
        layout.addWidget(self.order_table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_items_combo(self):
        """آپدیت لیست آیتم‌ها براساس دسته‌بندی انتخاب‌شده"""
        category = self.category_combo.currentText()
        self.item_combo.clear()
        for item in MENU[category]:
            self.item_combo.addItem(item["name"])

    def add_to_order(self):
        """اضافه کردن آیتم به سفارش"""
        category = self.category_combo.currentText()
        item_name = self.item_combo.currentText()
        quantity = self.quantity_spin.value()

        # پیدا کردن قیمت آیتم
        price = next(
            item["price"] for item in MENU[category] 
            if item["name"] == item_name
        )

        # اضافه به لیست سفارش
        self.order_items.append({
            "name": item_name,
            "quantity": quantity,
            "price": price
        })

        # آپدیت جدول
        self.update_order_table()

    def update_order_table(self):
        """نمایش سفارشات در جدول"""
        self.order_table.setRowCount(len(self.order_items))
        for row, item in enumerate(self.order_items):
            self.order_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.order_table.setItem(row, 1, QTableWidgetItem(str(item["quantity"])))
            self.order_table.setItem(row, 2, QTableWidgetItem(f"{item['price'] * item['quantity']:,} تومان"))
        