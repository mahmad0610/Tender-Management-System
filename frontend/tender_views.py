from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFrame, QLineEdit, QComboBox)
from PySide6.QtCore import Qt
import requests
from .tender_dialogs import TenderFormDialog

API_URL = "http://localhost:8000"

class TenderListView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header & Filters
        header_layout = QHBoxLayout()
        title = QLabel("Tender Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        if self.user_data['role'] in ['client', 'admin']:
            create_btn = QPushButton("Create New Tender")
            create_btn.setStyleSheet("background-color: #2563eb; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px;")
            create_btn.clicked.connect(self.handle_create)
            header_layout.addWidget(create_btn)
            
        layout.addLayout(header_layout)
        
        # Filter Bar
        filter_bar = QFrame()
        filter_bar.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e5e7eb; margin: 10px 0;")
        fb_layout = QHBoxLayout(filter_bar)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID or Title...")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Statuses", "Open", "Under Review", "Approved", "Rejected"])
        
        refresh_btn = QPushButton("Apply Filters")
        refresh_btn.clicked.connect(self.load_tenders)
        
        fb_layout.addWidget(QLabel("Search:"))
        fb_layout.addWidget(self.search_input)
        fb_layout.addWidget(QLabel("Status:"))
        fb_layout.addWidget(self.status_filter)
        fb_layout.addWidget(refresh_btn)
        
        layout.addWidget(filter_bar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tender ID", "Title", "Vendor/Client", "Status", "Submission Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 8px;")
        
        layout.addWidget(self.table)
        
        self.load_tenders()

    def load_tenders(self):
        try:
            res = requests.get(f"{API_URL}/tenders/")
            if res.status_code == 200:
                tenders = res.json()
                self.table.setRowCount(len(tenders))
                for i, t in enumerate(tenders):
                    self.table.setItem(i, 0, QTableWidgetItem(t['tender_id']))
                    self.table.setItem(i, 1, QTableWidgetItem(t['title']))
                    self.table.setItem(i, 2, QTableWidgetItem(str(t.get('client_id', 'N/A'))))
                    self.table.setItem(i, 3, QTableWidgetItem(t['status'].upper()))
                    self.table.setItem(i, 4, QTableWidgetItem(t['created_at'][:10]))
        except Exception as e:
            print(f"Error loading tenders: {e}")

    def handle_create(self):
        dialog = TenderFormDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                # Add client_id from user_data
                data['client_id'] = self.user_data['id']
                data['tender_id'] = f"T-{requests.get(f'{API_URL}/tenders/').json().__len__() + 1001}"
                
                res = requests.post(f"{API_URL}/tenders/", json=data)
                if res.status_code == 200:
                    self.load_tenders()
                    QMessageBox.information(self, "Success", "Tender created successfully!")
                else:
                    error_msg = res.json().get('detail', res.text)
                    QMessageBox.warning(self, "Failure", f"Failed to create tender: {error_msg}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to connect to server: {e}")
