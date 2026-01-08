from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QFormLayout, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QFileDialog, QMessageBox, QDateEdit, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, QDate
import requests

API_URL = "http://localhost:8000"

class OrderGenerationView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Order Generation")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        f_layout = QFormLayout(form_frame)
        
        self.tender_ref = QComboBox()
        self.tender_ref.setEditable(True)
        self.tender_ref.setPlaceholderText("Select Tender Reference...")
        self.order_num = QLineEdit()
        self.order_num.setPlaceholderText("Enter Order Number...")
        self.order_date = QDateEdit(QDate.currentDate())
        self.approved_by = QLineEdit()

        f_layout.addRow("Tender Reference:", self.tender_ref)
        f_layout.addRow("Order Number:", self.order_num)
        f_layout.addRow("Order Date:", self.order_date)

        f_layout.addRow("Approved By (Technical/Finance):", self.approved_by)
        
        self.items_input = QTextEdit()
        self.items_input.setMaxHeight(60)
        self.items_input.setPlaceholderText("Enter line items...")
        f_layout.addRow("Items:", self.items_input)

        self.ack_box = QCheckBox("Vendor Acknowledged PO (Yes/No)")
        f_layout.addRow("", self.ack_box)

        confirm_btn = QPushButton("Confirm & Issue Purchase Order")
        confirm_btn.setStyleSheet("background-color: #1e3a8a; color: white; padding: 12px; font-weight: bold;")
        confirm_btn.clicked.connect(self.handle_po_issue)
        f_layout.addRow("", confirm_btn)

        layout.addWidget(form_frame)
        layout.addStretch()

        # populate tenders and vendors
        self.load_tenders_and_vendors()

    def load_tenders_and_vendors(self):
        try:
            tres = requests.get(f"{API_URL}/tenders/")
            if tres.status_code == 200:
                tenders = tres.json()
                self.tender_ref.clear()
                for t in tenders:
                    # show readable label, keep id in userData
                    self.tender_ref.addItem(f"{t['tender_id']} - {t['title']}", t['id'])
            ures = requests.get(f"{API_URL}/users/")
            self._vendors = []
            if ures.status_code == 200:
                users = ures.json()
                self._vendors = [u for u in users if u['role'] == 'vendor']
        except Exception as e:
            print('Failed to load tenders/vendors:', e)

    def handle_po_issue(self):
        if not self.ack_box.isChecked():
            QMessageBox.warning(self, "Pending", "Vendor must acknowledge PO before final issuance.")
        else:
            # get selected tender id
            try:
                tender_id = self.tender_ref.currentData()
            except Exception:
                tender_id = None
            vendor_id = self._vendors[0]['id'] if self._vendors else 0
            data = {
                "tender_id": tender_id or 0,
                "vendor_id": vendor_id,
                "po_number": self.order_num.text(),
                "items": self.items_input.toPlainText(),
                "total_amount": 0.0,
                "approved_by": self.approved_by.text()
            }
            try:
                res = requests.post(f"{API_URL}/purchase_orders/", json=data)
                if res.status_code == 200:
                    QMessageBox.information(self, "Success", "Purchase Order issued and logged in system.")
                    # refresh any local views if needed
                    self.load_tenders_and_vendors()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed: {e}")

class ContractManagementView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Contract Management")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        f_layout = QFormLayout(form_frame)
        
        # New: Select Tender to link contract
        self.tender_select = QComboBox()
        f_layout.addRow("Link to Tender:", self.tender_select)
        
        f_layout.addRow("Scope of Work:", QLineEdit(placeholderText="Define scope..."))
        f_layout.addRow("Start Date:", QDateEdit(QDate.currentDate()))
        f_layout.addRow("End Date:", QDateEdit(QDate.currentDate().addMonths(12)))
        
        self.vet_status = QLineEdit()
        f_layout.addRow("Legal Vetting Status:", self.vet_status)
        
        self.trans_id = QLineEdit()
        f_layout.addRow("Transmission ID:", self.trans_id)
        
        save_btn = QPushButton("Save & Dispatch Contract")
        save_btn.setStyleSheet("background-color: #1e3a8a; color: white; padding: 10px;")
        save_btn.clicked.connect(self.handle_save_contract)
        f_layout.addRow("", save_btn)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        
        self.load_tenders()

    def load_tenders(self):
        try:
            res = requests.get(f"{API_URL}/tenders/")
            if res.status_code == 200:
                tenders = res.json()
                self.tender_select.clear()
                for t in tenders:
                    self.tender_select.addItem(f"{t['tender_id']} - {t['title']}", t['id'])
        except: pass

    def handle_save_contract(self):
        tender_id = self.tender_select.currentData()
        if not tender_id:
            QMessageBox.warning(self, "Error", "Please select a tender.")
            return

        data = {
            "tender_id": tender_id,
            "content": "Full Master Services Agreement",
            "scope_of_work": "As defined...",
            "start_date": self.findChild(QDateEdit).date().toPython().isoformat(),
            "end_date": self.findChildren(QDateEdit)[1].date().toPython().isoformat(),
            "vetting_status": self.vet_status.text(),
            "dispatch_id": self.trans_id.text()
        }
        try:
            res = requests.post(f"{API_URL}/contracts/", json=data)
            if res.status_code == 200:
                QMessageBox.information(self, "Success", "Contract dispatched.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")

class DeliveryMilestoneView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        
        header = QLabel("Delivery & Quality Control")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        # Select Tender
        self.tender_select = QComboBox()
        self.tender_select.currentIndexChanged.connect(self.load_milestones)
        layout.addWidget(QLabel("Select Tender Project:"))
        layout.addWidget(self.tender_select)
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Milestone", "Status", "Delivery Note", "Inspection", "Quality Remarks", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        layout.addStretch()
        self.load_tenders()

    def load_tenders(self):
        try:
            res = requests.get(f"{API_URL}/tenders/")
            if res.status_code == 200:
                self.tender_select.clear()
                for t in res.json():
                    self.tender_select.addItem(f"{t['title']}", t['id'])
        except: pass

    def load_milestones(self):
        try:
            tid = self.tender_select.currentData()
            if not tid: return
            res = requests.get(f"{API_URL}/tenders/{tid}/milestones")
            if res.status_code == 200:
                self.populate_table(res.json())
        except: pass

    def populate_table(self, milestones):
        self.table.setRowCount(0)
        for row, m in enumerate(milestones):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(m['title']))
            self.table.setItem(row, 1, QTableWidgetItem(m['status']))
            self.table.setItem(row, 2, QTableWidgetItem(str(m.get('delivery_id') or 'Pending')))
            self.table.setItem(row, 3, QTableWidgetItem(m.get('inspection_status', 'Pending')))
            self.table.setItem(row, 4, QTableWidgetItem(m.get('quality_remarks', '')))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0,0,0,0)
            
            # Action logic based on role
            if self.user_data['role'] in ['vendor', 'admin']:
                up_btn = QPushButton("Upload")
                up_btn.clicked.connect(lambda _, mid=m['id']: self.handle_upload(mid))
                btn_layout.addWidget(up_btn)
            
            if self.user_data['role'] in ['client', 'technical', 'admin']:
                insp_btn = QPushButton("Inspect")
                insp_btn.clicked.connect(lambda _, mid=m['id']: self.handle_inspection(mid))
                btn_layout.addWidget(insp_btn)
                
            self.table.setCellWidget(row, 5, btn_widget)

    def handle_upload(self, mid):
        # Simulating upload
        try:
            requests.put(f"{API_URL}/milestones/{mid}", json={"delivery_id": "DEL-123", "status": "In Progress"})
            self.load_milestones()
        except: pass

    def handle_inspection(self, mid):
        # Simulating inspection pass
        try:
            requests.put(f"{API_URL}/milestones/{mid}", json={"inspection_status": "Passed", "status": "Completed"})
            self.load_milestones()
        except: pass

class BillingInvoiceView(QWidget):
    def __init__(self, user_data, is_finance=False):
        super().__init__()
        self.user_data = user_data
        self.is_finance = is_finance
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        
        title = "Invoice Generation" if self.is_finance else "Billing Draft Preparation"
        header = QLabel(title)
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        f_layout = QFormLayout(form_frame)
        
        self.po_select = QComboBox()
        f_layout.addRow("Reference (PO):", self.po_select)
        f_layout.addRow("Tax (%)", QLineEdit("18"))
        f_layout.addRow("Discount (%)", QLineEdit("0"))

        self.audit_flag = QCheckBox("Mark for Audit Review")
        f_layout.addRow("", self.audit_flag)

        self.ver_date = QDateEdit(QDate.currentDate())
        f_layout.addRow("Verification Date:", self.ver_date)

        instruction = QLabel("Admin Dept provides delivery details. Finance finalizes docs.")
        instruction.setStyleSheet("color: #64748b; font-style: italic;")
        f_layout.addRow("", instruction)

        btn_text = "Issue Final Audited Invoice" if self.is_finance else "Submit Billing Draft"
        action_btn = QPushButton(btn_text)
        action_btn.setStyleSheet("background-color: #1e3a8a; color: white; padding: 12px;")
        action_btn.clicked.connect(self.handle_invoice_gen)
        f_layout.addRow("", action_btn)

        if self.is_finance:
            download_btn = QPushButton("Download Final Invoice PDF")
            f_layout.addRow("", download_btn)

        # load purchase orders for selection
        self.load_purchase_orders()

        layout.addWidget(form_frame)
        layout.addStretch()

    def handle_invoice_gen(self):
        try:
            po_id = self.po_select.currentData() or 0
        except Exception:
            po_id = 0
        data = {
            "po_id": po_id,
            "po_id": po_id,
            # "invoice_number": Auto generated
            "amount": 10000.0,
            "total_payable": 11800.0,
            "issuance_id": f"ISS-{100}",
            "audit_flag": 1 if self.audit_flag.isChecked() else 0,
            "verification_date": self.ver_date.date().toPython().isoformat()
        }
        try:
            res = requests.post(f"{API_URL}/invoices/", json=data)
            if res.status_code == 200:
                QMessageBox.information(self, "Success", "Final audited invoice issued.")
        except: pass

    def load_purchase_orders(self):
        try:
            res = requests.get(f"{API_URL}/purchase_orders/")
            if res.status_code == 200:
                pos = res.json()
                self.po_select.clear()
                for po in pos:
                    self.po_select.addItem(f"{po.get('po_number','PO-'+str(po['id']))} - Tender {po.get('tender_id')}", po['id'])
        except Exception as e:
            print('Failed to load POs:', e)

class PaymentManagementView(QWidget):
    def __init__(self, user_data, is_recording=False):
        super().__init__()
        self.user_data = user_data
        self.is_recording = is_recording
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        
        title = "Payment Recording" if self.is_recording else "Payment Processing & Verification"
        header = QLabel(title)
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        f_layout = QFormLayout(form_frame)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        f_layout = QFormLayout(form_frame)
        # Removed text parsing

        if self.is_recording:
            self.invoice_select = QComboBox()
            f_layout.addRow("Invoice Ref:", self.invoice_select)
            self.payment_amount_input = QLineEdit()
            f_layout.addRow("Payment Amount:", self.payment_amount_input)
            mode_cb = QComboBox()
            mode_cb.addItems(["Bank Transfer", "Cheque", "Online"])
            f_layout.addRow("Payment Mode:", mode_cb)
            self.trans_id_input = QLineEdit()
            f_layout.addRow("Transfer ID:", self.trans_id_input)
            f_layout.addRow("Payment Proof:", QPushButton("Upload Proof (PDF/Image)"))

            btn = QPushButton("Initiate Payment ")
            btn.clicked.connect(self.handle_payment_init)
            f_layout.addRow("", btn)
            # populate invoice choices
            self.load_invoices_for_payment()
            layout.addWidget(form_frame)
            layout.addStretch()
        else:
            table = QTableWidget(0, 5)
            table.setHorizontalHeaderLabels(["Ref", "Amount", "Transfer ID", "System Record", "Action"])
            layout.addWidget(table)
            self.load_payments(table)

    def handle_payment_init(self):
        try:
            invoice_id = self.invoice_select.currentData() or 0
        except Exception:
            invoice_id = 0
        amt = float(self.payment_amount_input.text() or 0)
        data = {
            "invoice_id": invoice_id,
            "amount_paid": amt,
            "payment_mode": "Bank Transfer",
            "#transaction_id": "Auto-generated by backend",
            "transfer_id": self.trans_id_input.text(),
            "commission_amount": amt * 0.10 # 10% auto commission
        }
        try:
            res = requests.post(f"{API_URL}/payments/", json=data)
            if res.status_code == 200:
                QMessageBox.information(self, "Success", "Payment initiated and recorded.")
        except: pass

    def load_invoices_for_payment(self):
        try:
            r = requests.get(f"{API_URL}/invoices/")
            if r.status_code == 200:
                invs = r.json()
                self.invoice_select.clear()
                for inv in invs:
                    self.invoice_select.addItem(f"{inv.get('invoice_number','INV-'+str(inv['id']))} - ${inv.get('total_payable',0)}", inv['id'])
        except Exception as e:
            print('Failed to load invoices:', e)

    def load_payments(self, table):
        try:
            res = requests.get(f"{API_URL}/payments/")
            if res.status_code == 200:
                payments = res.json()
                table.setRowCount(len(payments))
                for i, p in enumerate(payments):
                    table.setItem(i, 0, QTableWidgetItem(f"P-{p['id']}"))
                    table.setItem(i, 1, QTableWidgetItem(f"$ {p['amount_paid']:,.2f}"))
                    table.setItem(i, 2, QTableWidgetItem(p.get('transfer_id', '')))
                    table.setItem(i, 3, QTableWidgetItem(p['status']))
                    
                    btn = QPushButton("Verify")
                    btn.clicked.connect(lambda _, pid=p['id']: self.handle_verify(pid))
                    table.setCellWidget(i, 4, btn)
        except: pass

    def handle_verify(self, pid):
        try:
            res = requests.put(f"{API_URL}/payments/{pid}/verify")
            if res.status_code == 200:
                QMessageBox.information(self, "Success", "Payment reconciled and verified.")
        except: pass
            
        layout.addWidget(form_frame)
        layout.addStretch()
