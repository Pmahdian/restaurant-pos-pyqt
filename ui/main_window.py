from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView, QSpinBox, QMessageBox,
    QToolBar, QDialog, QStackedWidget
)
from PyQt6.QtCore import Qt
from datetime import datetime
from core.printer import generate_invoice_pdf
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم فروش رستوران")
        self.current_order = []
        self.temp_invoices = []
        self.invoice_counter = 1
        self.setup_ui()

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
        
        # دکمه بازگشت به سفارش‌گیری
        order_btn = QPushButton("سفارش جدید")
        order_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        toolbar.addWidget(order_btn)
        
        # دکمه گزارش فروش
        report_btn = QPushButton("گزارش فروش روزانه")
        report_btn.clicked.connect(self.show_daily_sales)
        toolbar.addWidget(report_btn)
        
        # دکمه حذف همه
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
        
        # --- بخش منو و سفارش ---
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

    # بقیه متدها (add_to_order, remove_item, calculate_total, etc.) 
    # همانند نسخه قبلی باقی می‌مانند
    
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
        table.setColumnCount(6)
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
    
    # بقیه متدها (save_permanent, print_report, clear_all_data, etc.)
    # همانند نسخه قبلی باقی می‌مانند