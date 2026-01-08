from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QScrollArea, QFrame)
from PySide6.QtCore import Qt
from .components import StatCard, ActionCard
import requests

API_URL = "http://localhost:8000"

class FinanceDashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Stats
        stats_layout = QHBoxLayout()
        self.inv_pending = StatCard("Pending Invoices", "0", "#2563eb")
        self.pay_received = StatCard("Payments Received", "$ 0", "#059669")
        self.out_balance = StatCard("Outstanding Balance", "$ 0", "#dc2626")
        
        stats_layout.addWidget(self.inv_pending)
        stats_layout.addWidget(self.pay_received)
        stats_layout.addWidget(self.out_balance)
        layout.addLayout(stats_layout)

        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(ActionCard("Verify Payments", "Match bank transactions", "#eff6ff", "#2563eb"))
        actions_layout.addWidget(ActionCard("Generate Billing", "Process POs to Invoices", "#f0fdf4", "#059669"))
        actions_layout.addWidget(ActionCard("Ledger View", "Full financial audit", "#fffbeb", "#d97706"))
        layout.addLayout(actions_layout)

        # Table
        table_label = QLabel("Recent Financial Transactions")
        table_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; margin-top: 20px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Entity", "Type", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        layout.addStretch()
        self.refresh_data()

    def refresh_data(self):
        try:
            # Fetch all invoices
            inv_res = requests.get(f"{API_URL}/invoices/")
            pay_res = requests.get(f"{API_URL}/payments/")
            
            if inv_res.status_code == 200 and pay_res.status_code == 200:
                invoices = inv_res.json()
                payments = pay_res.json()
                
                pending_invs = [inv for inv in invoices if inv['status'] != 'Paid']
                self.inv_pending.update_value(str(len(pending_invs)))
                
                verified_payments = [p for p in payments if p['status'] == 'Verified']
                total_received = sum(p['amount_paid'] for p in verified_payments)
                self.pay_received.update_value(f"$ {total_received:,.0f}")
                
                total_outstanding = sum(inv['total_payable'] for inv in pending_invs)
                self.out_balance.update_value(f"$ {total_outstanding:,.0f}")
                
                # Populate table with recent payments
                self.table.setRowCount(len(payments))
                for i, p in enumerate(reversed(payments)):
                    if i >= 10: break # Show only last 10
                    self.table.setItem(i, 0, QTableWidgetItem(p['payment_date'][:10]))
                    self.table.setItem(i, 1, QTableWidgetItem(f"Invoice #{p['invoice_id']}"))
                    self.table.setItem(i, 2, QTableWidgetItem(p['status']))
                    self.table.setItem(i, 3, QTableWidgetItem(f"$ {p['amount_paid']:,.0f}"))
        except Exception as e:
            print(f"Error refreshing finance dashboard: {e}")
