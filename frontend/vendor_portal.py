from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QScrollArea, QFrame)
from PySide6.QtCore import Qt
from .components import StatCard, ActionCard
import requests

API_URL = "http://localhost:8000"

class VendorPortal(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Stats
        stats_layout = QHBoxLayout()
        self.my_bids = StatCard("My Total Bids", "0", "#2563eb")
        self.app_pending = StatCard("Approved / Pending", "0 / 0", "#059669")
        self.pend_inv = StatCard("Pending Invoices", "0", "#d97706")
        
        stats_layout.addWidget(self.my_bids)
        stats_layout.addWidget(self.app_pending)
        stats_layout.addWidget(self.pend_inv)
        layout.addLayout(stats_layout)

        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(ActionCard("Browse Tenders", "Find new opportunities", "#eff6ff", "#2563eb"))
        actions_layout.addWidget(ActionCard("Upload Delivery", "Submit milestone proof", "#f0fdf4", "#059669"))
        actions_layout.addWidget(ActionCard("Payment Status", "Check remittance advice", "#fffbeb", "#d97706"))
        layout.addLayout(actions_layout)

        # Table
        table_label = QLabel("Recent Tender Submissions")
        table_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; margin-top: 20px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ref", "Project", "My Bid", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        layout.addStretch()
        self.refresh_data()

    def refresh_data(self):
        try:
            # Fetch all proposals
            res = requests.get(f"{API_URL}/proposals/")
            if res.status_code == 200:
                all_proposals = res.json()
                # Filter for this vendor
                my_props = [p for p in all_proposals if p['vendor_id'] == self.user_data['id']]
                
                self.table.setRowCount(len(my_props))
                for i, p in enumerate(my_props):
                    self.table.setItem(i, 0, QTableWidgetItem(f"T-{p['tender_id']}"))
                    self.table.setItem(i, 1, QTableWidgetItem("Tender Title")) # Ideally fetch tender title
                    self.table.setItem(i, 2, QTableWidgetItem(f"$ {p['financial_input']:,.0f}"))
                    self.table.setItem(i, 3, QTableWidgetItem(p['status'].upper()))
                
                self.my_bids.update_value(str(len(my_props)))
                approved = len([p for p in my_props if p['status'] == 'Approved'])
                pending = len([p for p in my_props if p['status'] not in ['Approved', 'Rejected']])
                self.app_pending.update_value(f"{approved} / {pending}")

                # Fetch invoices for this vendor
                po_res = requests.get(f"{API_URL}/purchase_orders/")
                inv_res = requests.get(f"{API_URL}/invoices/")
                if po_res.status_code == 200 and inv_res.status_code == 200:
                    my_pos = [po for po in po_res.json() if po['vendor_id'] == self.user_data['id']]
                    my_po_ids = [po['id'] for po in my_pos]
                    pending_invs = [inv for inv in inv_res.json() if inv['po_id'] in my_po_ids and inv['status'] != 'Paid']
                    self.pend_inv.update_value(str(len(pending_invs)))
        except Exception as e:
            print(f"Error refreshing vendor portal: {e}")
