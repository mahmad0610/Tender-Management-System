from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QScrollArea, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QTimer
import requests
from .components import StatCard, ActionCard
from .tender_dialogs import TenderFormDialog

API_URL = "http://localhost:8000"

class ClientPortal(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Stats
        stats_layout = QHBoxLayout()
        self.awaiting_app = StatCard("Awaiting Approval", "0", "#2563eb")
        self.active_contracts = StatCard("Active Contracts", "0", "#059669")
        self.pending_payments = StatCard("Pending Payments", "0", "#dc2626")
        
        stats_layout.addWidget(self.awaiting_app)
        stats_layout.addWidget(self.active_contracts)
        stats_layout.addWidget(self.pending_payments)
        layout.addLayout(stats_layout)

        # Actions
        actions_layout = QHBoxLayout()
        post_btn = ActionCard("Post a Requirement", "Launch a new tender", "#eff6ff", "#2563eb")
        post_btn.clicked.connect(self.handle_post_tender)
        actions_layout.addWidget(post_btn)
        actions_layout.addWidget(ActionCard("My Active Tenders", "Track existing tenders", "#f0fdf4", "#059669"))
        layout.addLayout(actions_layout)

        # Table
        table_label = QLabel("My Recent Tenders")
        table_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; margin-top: 20px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ref", "Title", "Status", "Deadline"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        layout.addStretch()
        self.refresh_data()

        # Auto refresh every 10 seconds so the UI reflects backend changes
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(10000)
        self._refresh_timer.timeout.connect(self.refresh_data)
        self._refresh_timer.start()

    def refresh_data(self):
        try:
            # Fetch tenders for this client
            res = requests.get(f"{API_URL}/tenders/")
            if res.status_code == 200:
                all_tenders = res.json()
                # Filter for this client
                my_tenders = [t for t in all_tenders if t.get('client_id') == self.user_data['id']]
                
                self.table.setRowCount(len(my_tenders))
                for i, t in enumerate(my_tenders):
                    self.table.setItem(i, 0, QTableWidgetItem(t['tender_id']))
                    self.table.setItem(i, 1, QTableWidgetItem(t['title']))
                    self.table.setItem(i, 2, QTableWidgetItem(t['status'].upper()))
                    self.table.setItem(i, 3, QTableWidgetItem(t['deadline'][:16].replace('T', ' ')))
                
                # Update stats with real counts
                self.awaiting_app.update_value(str(len([t for t in my_tenders if t['status'] == 'submitted'])))
                self.active_contracts.update_value(str(len([t for t in my_tenders if t['status'] == 'approved'])))
                
                # Fetch invoices to calculate real pending payments
                inv_res = requests.get(f"{API_URL}/invoices/")
                if inv_res.status_code == 200:
                    all_invoices = inv_res.json()
                    # Filter invoices for this client's tenders
                    my_tender_ids = [t['id'] for t in my_tenders]
                    # We need to know which POs belong to which tenders. 
                    # For simplicity, we'll fetch POs too or assume we can filter by po.tender_id.
                    po_res = requests.get(f"{API_URL}/purchase_orders/")
                    if po_res.status_code == 200:
                        all_pos = po_res.json()
                        my_po_ids = [po['id'] for po in all_pos if po['tender_id'] in my_tender_ids]
                        my_invoices = [inv for inv in all_invoices if inv['po_id'] in my_po_ids and inv['status'] != 'Paid']
                        total_pending = sum(inv['total_payable'] for inv in my_invoices)
                        self.pending_payments.update_value(f"$ {total_pending:,.0f}")
        except Exception as e:
            print(f"Error refreshing client portal: {e}")

    def handle_post_tender(self):
        dialog = TenderFormDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                data['client_id'] = self.user_data['id']
                data['tender_id'] = f"T-{requests.get(f'{API_URL}/tenders/').json().__len__() + 1001}"
                
                res = requests.post(f"{API_URL}/tenders/", json=data)
                if res.status_code == 200:
                    self.refresh_data()
                    QMessageBox.information(self, "Success", "Tender created successfully!")
                else:
                    error_msg = res.json().get('detail', res.text)
                    QMessageBox.warning(self, "Failure", f"Failed to create tender: {error_msg}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to connect to server: {e}")
