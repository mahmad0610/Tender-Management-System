from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFrame, QComboBox, QDateEdit, QFormLayout, QLineEdit)
from PySide6.QtCore import Qt, QDate
import requests

API_URL = "http://localhost:8000"

class ReportsAnalyticsView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Reports & Analytics")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        # Filter Bar
        filter_bar = QFrame()
        filter_bar.setStyleSheet("background-color: white; border-radius: 12px; padding: 15px;")
        fb_layout = QHBoxLayout(filter_bar)
        
        fb_layout.addWidget(QLabel("Date From:"))
        fb_layout.addWidget(QDateEdit(QDate.currentDate().addMonths(-1)))
        fb_layout.addWidget(QLabel("To:"))
        fb_layout.addWidget(QDateEdit(QDate.currentDate()))
        
        export_btn = QPushButton("Export Excel")
        export_btn.setStyleSheet("background-color: #059669; color: white;")
        fb_layout.addWidget(export_btn)
        
        layout.addWidget(filter_bar)
        
        # Summary Area
        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["Report Name", "Generated Date", "User", "Action"])
        table.setItem(0, 0, QTableWidgetItem("Monthly Revenue Summary"))
        table.setItem(1, 0, QTableWidgetItem("Vendor Performance Report"))
        table.setItem(2, 0, QTableWidgetItem("Tender Status Distribution"))
        
        layout.addWidget(table)
        layout.addStretch()

class AuditLogsView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Audit Logs")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        table = QTableWidget(10, 3)
        table.setHorizontalHeaderLabels(["Timestamp", "User Action", "Entity Modified"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        logs = [
            ["2026-01-04 16:50", "LOGIN", "User: admin"],
            ["2026-01-04 16:45", "TENDER_CREATED", "T-1025"],
            ["2026-01-04 16:40", "PAYMENT_RECORDED", "INV-8801"],
            ["2026-01-04 16:35", "STATUS_CHANGE", "T-990 -> Under Review"]
        ]
        
        for i, row in enumerate(logs):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(val))
                
        layout.addWidget(table)
        layout.addStretch()

class AdminSettingsView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("System Administration & Settings")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        f_layout = QFormLayout(form_frame)
        
        f_layout.addRow("System Name:", QLineEdit("Tender ERP Enterprise"))
        f_layout.addRow("Currency Code:", QComboBox())
        f_layout.addRow("Enable Auto-numbering:", QComboBox())
        f_layout.addRow("Notification Email:", QLineEdit("admin@tendererp.com"))
        
        save_btn = QPushButton("Apply System Configurations")
        save_btn.setStyleSheet("background-color: #1e3a8a; color: white; padding: 12px;")
        f_layout.addRow("", save_btn)
        
        layout.addWidget(form_frame)
        layout.addStretch()
