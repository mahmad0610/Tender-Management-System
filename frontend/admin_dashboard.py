from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QPushButton, QDialog)
from PySide6.QtCore import Qt
import requests
from .components import StatCard, ActionCard

API_URL = "http://localhost:8000"

class AdminDashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Stats Row
        stats_layout = QHBoxLayout()
        self.total_users = StatCard("Total Users", "0", "#2563eb")
        self.active_tenders = StatCard("Active Tenders", "0", "#059669")
        self.revenue_summary = StatCard("Revenue Summary", "$ 0", "#d97706")
        
        stats_layout.addWidget(self.total_users)
        stats_layout.addWidget(self.active_tenders)
        stats_layout.addWidget(self.revenue_summary)
        layout.addLayout(stats_layout)

        # Quick Actions
        actions_label = QLabel("Administrative Controls")
        actions_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; margin-top: 20px;")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(ActionCard("User Management", "Manage roles & permissions", "#eff6ff", "#2563eb"))
        actions_layout.addWidget(ActionCard("System Config", "Update system settings", "#f0fdf4", "#059669"))
        actions_layout.addWidget(ActionCard("Security Logs", "Audit user activities", "#fffbeb", "#d97706"))
        layout.addLayout(actions_layout)

        # Recent Tenders Table
        table_label = QLabel("Recent System Tenders")
        table_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; margin-top: 20px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Status", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        layout.addStretch()
        self.refresh_stats()

    def refresh_stats(self):
        try:
            users = requests.get(f"{API_URL}/users/").json()
            tenders = requests.get(f"{API_URL}/tenders/").json()
            self.total_users.update_value(str(len(users)))
            self.active_tenders.update_value(str(len(tenders)))
            
            # Fetch payments for revenue summary
            pay_res = requests.get(f"{API_URL}/payments/")
            if pay_res.status_code == 200:
                verified_payments = [p for p in pay_res.json() if p['status'] == 'Verified']
                total_rev = sum(p['amount_paid'] for p in verified_payments)
                self.revenue_summary.update_value(f"$ {total_rev:,.0f}")
            else:
                self.revenue_summary.update_value("$ 0")

            # Populate table
            self.table.setRowCount(len(tenders))
            for i, t in enumerate(tenders):
                self.table.setItem(i, 0, QTableWidgetItem(t['tender_id']))
                self.table.setItem(i, 1, QTableWidgetItem(t['title']))
                self.table.setItem(i, 2, QTableWidgetItem(t['status'].upper()))
                self.table.setItem(i, 3, QTableWidgetItem(t['created_at'][:10]))
        except Exception as e:
            print(f"Error refreshing admin stats: {e}")
