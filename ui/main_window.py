from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QHeaderView, QSpinBox, QMessageBox,
    QToolBar, QDialog, QInputDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime
from core.printer import generate_invoice_pdf
import os
import json
from database.models import save_invoice_to_db

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم فروش رستوران")
        self.current_order = []
        self.temp_invoices = []
        self.invoice_counter = 1
        self.setup_ui()

    def setup_ui(self):
        toolbar = QToolBar("ابزارهای اصلی")
        self.addToolBar(toolbar)

        self.new_order_btn = QPushButton("سفارش جدید")
        self.new_order_btn.clicked.connect(self.reset_order)
        toolbar.addWidget(self.new_order_btn)

        self.report_btn = QPushButton("گزارش فروش")
        self.report_btn.clicked.connect(self.show_daily_sales)
        toolbar.addWidget(self.report_btn)

        main_widget = QWidget()
        layout = QVBoxLayout()

        self.invoice_label = QLabel(f"فاکتور # {self.invoice_counter}")
        self.invoice_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        layout.addWidget(self.invoice_label)

        order_layout = QHBoxLayout()

        self.categories_tabs = QTabWidget()
        self.categories_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.setup_menu_tabs()
        order_layout.addWidget(self.categories_tabs, 1)

        right_section = QVBoxLayout()

        # تغییر: 5 ستون برای اضافه کردن توضیحات
        self.order_table = QTableWidget(0, 5)
        self.order_table.setHorizontalHeaderLabels(["آیتم", "قیمت", "تعداد", "توضیحات", "حذف"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        right_section.addWidget(self.order_table)

        calc_layout = QVBoxLayout()

        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("حق سرویس (%):"))
        self.service_spin = QSpinBox()
        self.service_spin.setRange(0, 30)
        self.service_spin.setValue(10)
        self.service_spin.valueChanged.connect(self.calculate_total)
        service_layout.addWidget(self.service_spin)

        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("تخفیف (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.valueChanged.connect(self.calculate_total)
        discount_layout.addWidget(self.discount_spin)

        self.total_label = QLabel("جمع کل: 0 تومان")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #27ae60;")

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
        self.current_order = []
        self.order_table.setRowCount(0)
        self.total_label.setText("جمع کل: 0 تومان")
        self.service_spin.setValue(10)
        self.discount_spin.setValue(0)
        self.invoice_counter += 1
        self.invoice_label.setText(f"فاکتور # {self.invoice_counter}")

    def setup_menu_tabs(self):
        from database.models import MENU
        
        for category, items in MENU.items():
            tab = QWidget()
            layout = QVBoxLayout()
            
            for item in items:
                btn_text = f"{item['name']}\n{item['price']:,} تومان"
                if item.get('description'):
                    btn_text += f"\n({item['description']})"
                btn = QPushButton(btn_text)
                btn.setMinimumHeight(60)
                btn.clicked.connect(lambda _, item=item: self.add_to_order(item))
                layout.addWidget(btn)
            
            tab.setLayout(layout)
            self.categories_tabs.addTab(tab, category)

    def add_to_order(self, item):
        # درخواست توضیحات از کاربر
        description, ok = QInputDialog.getText(
            self, 
            'توضیحات آیتم', 
            f'توضیحات برای {item["name"]}:',
            text=item.get('description', '')
        )
        if not ok:
            return
        
        existing = next((i for i in self.current_order if i["id"] == item["id"]), None)
        if existing:
            existing["quantity"] += 1
            existing["description"] = description
        else:
            self.current_order.append({
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": 1,
                "description": description
            })
        self.update_order_table()

    def update_order_table(self):
        self.order_table.setRowCount(len(self.current_order))
        for row, item in enumerate(self.current_order):
            self.order_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.order_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:,}"))
            self.order_table.setItem(row, 2, QTableWidgetItem(str(item["quantity"])))
            self.order_table.setItem(row, 3, QTableWidgetItem(item.get("description", "")))
            
            remove_btn = QPushButton("حذف")
            remove_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            remove_btn.clicked.connect(lambda _, r=row: self.remove_item(r))
            self.order_table.setCellWidget(row, 4, remove_btn)
        
        self.calculate_total()

    def remove_item(self, row):
        if 0 <= row < len(self.current_order):
            self.current_order.pop(row)
            self.update_order_table()

    def calculate_total(self):
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
        if not self.current_order:
            QMessageBox.warning(self, "خطا", "سبد خرید خالی است!")
            return
            
        try:
            total, service_fee, discount = self.calculate_total()
            invoice_id = self.save_invoice_action(total, service_fee, discount)
            
            # چاپ دو نسخه فاکتور
            self.print_to_pos_printer(total, invoice_id)
            
            QMessageBox.information(self, "موفق", "فاکتورها چاپ و ذخیره شدند")
            self.reset_order()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ فاکتور:\n{str(e)}")

    def save_invoice_action(self, total, service_fee, discount):
        invoice = {
            "id": self.invoice_counter,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.current_order.copy(),
            "total": total,
            "service_fee": service_fee,
            "discount": discount,
        }
        self.temp_invoices.append(invoice)
        
        invoice_id = save_invoice_to_db(
            self.current_order,
            total,
            service_fee,
            discount
        )
        return invoice_id

    def print_to_pos_printer(self, total, invoice_id):
        try:
            # چاپ نسخه مشتری
            print("\n\n------ چاپ به پرینتر (نسخه مشتری) ------")
            print(f"فاکتور # {invoice_id}")
            print(f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}")
            print("--------------------------")
            for item in self.current_order:
                print(f"{item['name']} {item['quantity']} × {item['price']:,} = {item['price'] * item['quantity']:,}")
                if item.get('description'):
                    print(f"  توضیحات: {item['description']}")
            print("--------------------------")
            print(f"جمع جزء: {sum(item['price'] * item['quantity'] for item in self.current_order):,}")
            print(f"حق سرویس: {service_fee:,}")
            print(f"تخفیف: {discount:,}")
            print(f"جمع کل: {total:,} تومان")
            print("------ با تشکر ------")
            print("\n\n")
            
            # چاپ نسخه آشپزخانه
            print("\n\n------ چاپ به پرینتر (نسخه آشپزخانه) ------")
            print(f"شماره سفارش: {invoice_id}")
            print(f"زمان: {datetime.now().strftime('%H:%M')}")
            print("--------------------------")
            for item in self.current_order:
                print(f"{item['name']} × {item['quantity']}")
                if item.get('description'):
                    print(f"  توضیحات: {item['description']}")
            print("--------------------------")
            print("زمان تحویل: ______")
            print("\n\n")
            
            # ایجاد نسخه PDF پشتیبان
            self.generate_backup_pdf(invoice_id, total)
        except Exception as e:
            raise Exception(f"خطا در چاپگر: {str(e)}")

    def generate_backup_pdf(self, invoice_id, total):
        try:
            os.makedirs("فاکتورهای_چاپی", exist_ok=True)
            from core.printer import generate_invoice_pdf
            generate_invoice_pdf(
                self.current_order,
                f"فاکتورهای_چاپی/فاکتور_{invoice_id}.pdf",
                invoice_id,
                datetime.now().strftime("%Y/%m/%d %H:%M"),
                total
            )
        except Exception as e:
            print(f"خطا در ایجاد نسخه PDF: {str(e)}")

    def show_daily_sales(self):
        if not self.temp_invoices:
            QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش وجود ندارد")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("گزارش فروش روزانه")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        daily_total = sum(inv["total"] for inv in self.temp_invoices)
        total_label = QLabel(f"<h2>جمع کل فروش روز: {daily_total:,} تومان</h2>")
        layout.addWidget(total_label)

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["شماره", "تاریخ", "تعداد آیتم", "جمع کل", "جزئیات", "چاپ مجدد"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        table.setRowCount(len(self.temp_invoices))
        for row, inv in enumerate(self.temp_invoices):
            table.setItem(row, 0, QTableWidgetItem(str(inv["id"])))
            table.setItem(row, 1, QTableWidgetItem(inv["date"]))
            table.setItem(row, 2, QTableWidgetItem(str(len(inv["items"]))))
            table.setItem(row, 3, QTableWidgetItem(f"{inv['total']:,}"))

            details_btn = QPushButton("مشاهده")
            details_btn.setStyleSheet("background-color: #f39c12; color: white;")
            details_btn.clicked.connect(lambda _, inv=inv: self.show_invoice_details(inv))
            table.setCellWidget(row, 4, details_btn)

            reprint_btn = QPushButton("چاپ مجدد")
            reprint_btn.setStyleSheet("background-color: #3498db; color: white;")
            reprint_btn.clicked.connect(lambda _, inv=inv: self.reprint_invoice(inv))
            table.setCellWidget(row, 5, reprint_btn)

        table.resizeColumnsToContents()
        layout.addWidget(table)

        save_btn = QPushButton("ذخیره گزارش کامل")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        save_btn.clicked.connect(self.save_full_report)
        layout.addWidget(save_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def show_invoice_details(self, invoice):
        details = "جزئیات فاکتور:\n\n"
        details += f"شماره فاکتور: {invoice['id']}\n"
        details += f"تاریخ: {invoice['date']}\n"
        details += "------------------------\n"
        
        for item in invoice["items"]:
            details += f"{item['name']} {item['quantity']} × {item['price']:,} = {item['price'] * item['quantity']:,}\n"
            if item.get('description'):
                details += f"  توضیحات: {item['description']}\n"
            details += "------------------------\n"
        
        details += f"جمع جزء: {sum(item['price'] * item['quantity'] for item in invoice['items']):,}\n"
        details += f"حق سرویس: {invoice['service_fee']:,}\n"
        details += f"تخفیف: {invoice['discount']:,}\n"
        details += f"جمع کل: {invoice['total']:,}"
        
        QMessageBox.information(self, f"جزئیات فاکتور #{invoice['id']}", details)

    def reprint_invoice(self, invoice):
        try:
            self.print_to_pos_printer(invoice["total"], invoice["id"])
            QMessageBox.information(self, "موفق", f"فاکتور #{invoice['id']} با موفقیت چاپ مجدد شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ مجدد:\n{str(e)}")

    def save_full_report(self):
        try:
            from openpyxl import Workbook
            import os
            
            os.makedirs("گزارشات_روزانه", exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"گزارشات_روزانه/گزارش_{date_str}.xlsx"
            
            wb = Workbook()
            ws = wb.active
            ws.title = "گزارش فروش"
            
            headers = [
                "شماره فاکتور", "تاریخ", "آیتم", 
                "تعداد", "قیمت واحد", "توضیحات", "جمع جزء",
                "حق سرویس", "تخفیف", "جمع کل"
            ]
            ws.append(headers)
            
            for inv in self.temp_invoices:
                for item in inv["items"]:
                    row = [
                        inv["id"],
                        inv["date"],
                        item["name"],
                        item["quantity"],
                        item["price"],
                        item.get("description", ""),
                        item["price"] * item["quantity"],
                        inv["service_fee"],
                        inv["discount"],
                        inv["total"]
                    ]
                    ws.append(row)
            
                ws.append([])
            
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