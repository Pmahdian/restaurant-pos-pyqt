from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, 
    QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit,
    QDoubleSpinBox, QLabel
)
from database.models import Item

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("رستوران من - سیستم صندوق")
        self.setGeometry(100, 100, 800, 600)
        
        # تب‌های اصلی
        self.tabs = QTabWidget()
        
        # تب منو
        self.setup_menu_tab()
        
        # تب سفارشات
        self.setup_order_tab()
        
        self.setCentralWidget(self.tabs)
    
    def setup_menu_tab(self):
        """تنظیم تب مدیریت منو"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # فرم اضافه کردن آیتم
        self.item_name = QLineEdit()
        self.item_price = QDoubleSpinBox()
        self.item_price.setMaximum(999999)
        add_btn = QPushButton("اضافه کردن آیتم")
        add_btn.clicked.connect(self.add_item)
        
        # جدول نمایش آیتم‌ها
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(2)
        self.items_table.setHorizontalHeaderLabels(["نام", "قیمت"])
        
        layout.addWidget(QLabel("آیتم جدید:"))
        layout.addWidget(self.item_name)
        layout.addWidget(QLabel("قیمت:"))
        layout.addWidget(self.item_price)
        layout.addWidget(add_btn)
        layout.addWidget(self.items_table)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "مدیریت منو")
    
    def add_item(self):
        """اضافه کردن آیتم جدید به منو"""
        name = self.item_name.text()
        price = self.item_price.value()
        
        if name and price > 0:
            item = Item(name, price)
            item.save()
            self.load_items()
            self.item_name.clear()
            self.item_price.setValue(0)
    
    def load_items(self):
        """بارگذاری آیتم‌ها در جدول"""
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
        conn.close()
        
        self.items_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item[1]))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item[2])))
    
    def setup_order_tab(self):
        """تنظیم تب سفارشات"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # پیاده‌سازی رابط سفارشات اینجا
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "ثبت سفارش")