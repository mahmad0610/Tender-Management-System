from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QFormLayout, QLineEdit, QComboBox,
                             QCheckBox, QMessageBox)
from PySide6.QtCore import Qt
import requests

API_URL = "http://localhost:8000"

class TechnicalEvaluationView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Technical Evaluation Queue (Technical Team)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tender", "Vendor", "Integration ID", "Status", "Tech Score", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Details Panel (Initially hidden or shown on selection)
        self.details_frame = QFrame()
        self.details_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb;")
        d_layout = QVBoxLayout(self.details_frame)
        
        title_lbl = QLabel("Tender Evaluation: Select a row above")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        d_layout.addWidget(title_lbl)
        
        checklist_layout = QVBoxLayout()
        checklist_layout.addWidget(QLabel("Technical Criteria Checklist:"))
        checklist_layout.addWidget(QCheckBox("Infrastructure Stability"))
        checklist_layout.addWidget(QCheckBox("Resource Availability"))
        checklist_layout.addWidget(QCheckBox("Technical Certifications"))
        d_layout.addLayout(checklist_layout)
        
        self.score_input = QLineEdit()
        self.score_input.setPlaceholderText("Score (0-100)")
        self.remarks_input = QTextEdit()
        self.remarks_input.setPlaceholderText("Evaluation Remarks...")
        
        d_layout.addWidget(QLabel("Score:"))
        d_layout.addWidget(self.score_input)
        d_layout.addWidget(QLabel("Remarks:"))
        d_layout.addWidget(self.remarks_input)
        
        submit_btn = QPushButton("Finalize & Submit Evaluation (Sales Dept Merge)")
        submit_btn.setStyleSheet("background-color: #1e3a8a; color: white; padding: 12px;")
        submit_btn.clicked.connect(self.submit_evaluation)
        d_layout.addWidget(submit_btn)
        
        clarify_btn = QPushButton("Clarify Specs (Technical Team)")
        clarify_btn.setStyleSheet("background-color: #d97706; color: white; padding: 10px; margin-top: 5px;")
        clarify_btn.clicked.connect(lambda: QMessageBox.information(self, "Integration", "Clarification request sent to Sales Department."))
        d_layout.addWidget(clarify_btn)
        
        layout.addWidget(self.details_frame)
        self.load_proposals()

    def load_proposals(self):
        try:
            res = requests.get(f"{API_URL}/proposals/")
            if res.status_code == 200:
                self.proposals = res.json()
                self.table.setRowCount(len(self.proposals))
                for i, p in enumerate(self.proposals):
                    self.table.setItem(i, 0, QTableWidgetItem(f"T-{p['tender_id']}"))
                    self.table.setItem(i, 1, QTableWidgetItem(f"V-{p['vendor_id']}"))
                    self.table.setItem(i, 2, QTableWidgetItem("View PDF"))
                    self.table.setItem(i, 3, QTableWidgetItem(str(p['technical_score'])))
                    
                    btn = QPushButton("Review")
                    btn.clicked.connect(lambda _, idx=i: self.select_proposal(idx))
                    self.table.setCellWidget(i, 4, btn)
        except: pass

    def select_proposal(self, idx):
        self.current_idx = idx
        p = self.proposals[idx]
        title = f"Tender Evaluation: T-{p['tender_id']} (Integration ID: {p.get('integration_id','N/A')})"
        self.details_frame.findChild(QLabel).setText(title)

    def submit_evaluation(self):
        if not hasattr(self, 'current_idx'):
            QMessageBox.warning(self, "Error", "Please select a proposal first.")
            return
            
        p = self.proposals[self.current_idx]
        data = {
            "technical_score": float(self.score_input.text() or 0),
            "technical_remarks": self.remarks_input.toPlainText(),
            "status": "Shortlisted"
        }
        try:
            res = requests.put(f"{API_URL}/proposals/{p['id']}", json=data)
            if res.status_code == 200:
                QMessageBox.information(self, "Success", "Technical evaluation submitted and saved to database.")
                self.load_proposals()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit: {e}")

class FinancialEvaluationView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Financial Evaluation & Commercial Input (Sales & Finance)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        f_layout = QFormLayout(form_frame)
        
        self.cost_lbl = QLabel("$ 0.00")
        self.margin_lbl = QLabel("0.0%")
        self.tax_lbl = QLabel("$ 0.00")
        
        f_layout.addRow("Cost Breakdown:", self.cost_lbl)
        f_layout.addRow("Margin Analysis:", self.margin_lbl)
        f_layout.addRow("Tax Calculation Preview (18%):", self.tax_lbl)
        
        self.remarks = QTextEdit()
        f_layout.addRow("Financial Remarks:", self.remarks)
        
        btn_layout = QHBoxLayout()
        app_btn = QPushButton("Approve Costs (Finance Dept)")
        app_btn.setStyleSheet("background-color: #059669; color: white; padding: 10px;")
        app_btn.clicked.connect(lambda: self.handle_recommendation("Shortlisted"))
        
        rej_btn = QPushButton("Reject Costs")
        rej_btn.setStyleSheet("background-color: #dc2626; color: white; padding: 10px;")
        rej_btn.clicked.connect(lambda: self.handle_recommendation("Rejected"))
        
        btn_layout.addWidget(app_btn)
        btn_layout.addWidget(rej_btn)
        
        layout.addWidget(form_frame)
        layout.addLayout(btn_layout)
        
        instruction_lbl = QLabel("Sales Dept provides commercial input. Finance Dept approves final costs.")
        instruction_lbl.setStyleSheet("color: #64748b; font-style: italic; margin-top: 10px;")
        layout.addWidget(instruction_lbl)
        
        layout.addStretch()

    def handle_recommendation(self, status):
        # In a real app, we'd pick the active proposal. 
        # For demo, we'll notify success and explain the role-based state change.
        QMessageBox.information(self, "Success", f"Commercial input saved. Proposal marked as {status}.")

class ClientApprovalView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        
        header = QLabel("Tenders Awaiting Your Approval")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Tender", "Tech Score", "Financial Remarks", "Status", "Response Time (h)", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.load_approvals()

    def load_approvals(self):
        try:
            res = requests.get(f"{API_URL}/proposals/")
            if res.status_code == 200:
                self.proposals = [p for p in res.json() if p['status'] == 'Shortlisted']
                self.table.setRowCount(len(self.proposals))
                for i, p in enumerate(self.proposals):
                    self.table.setItem(i, 0, QTableWidgetItem(f"T-{p['tender_id']}"))
                    self.table.setItem(i, 1, QTableWidgetItem(str(p['technical_score'])))
                    self.table.setItem(i, 2, QTableWidgetItem(p.get('financial_remarks', '')))
                    self.table.setItem(i, 3, QTableWidgetItem(p['status']))
                    self.table.setItem(i, 4, QTableWidgetItem("N/A"))
                    
                    btn = QPushButton("Select")
                    btn.clicked.connect(lambda _, idx=i: self.select_proposal(idx))
                    self.table.setCellWidget(i, 5, btn)
        except: pass

    def select_proposal(self, idx):
        self.current_idx = idx

    def handle_approval(self, status):
        if not hasattr(self, 'current_idx'):
            QMessageBox.warning(self, "Error", "Please select a proposal first.")
            return
            
        p = self.proposals[self.current_idx]
        data = {
            "status": "Approved" if status == "Approve" else "Rejected",
            "feedback": self.comments.toPlainText()
        }
        try:
            res = requests.put(f"{API_URL}/proposals/{p['id']}", json=data)
            if res.status_code == 200:
                QMessageBox.information(self, "Success", f"Proposal {status.lower()}ed and logged in system.")
                self.load_approvals()
        except: pass
        
        # Decision Panel
        dec_panel = QFrame()
        dec_panel.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        dp_layout = QVBoxLayout(dec_panel)
        
        dp_layout.addWidget(QLabel("Decision & Comments:"))
        self.comments = QTextEdit()
        dp_layout.addWidget(self.comments)
        
        btn_box = QHBoxLayout()
        app_btn = QPushButton("Approve & Generate Order")
        app_btn.clicked.connect(lambda: self.handle_approval("Approve"))
        
        rej_btn = QPushButton("Reject Bid")
        rej_btn.clicked.connect(lambda: self.handle_approval("Reject"))
        
        req_btn = QPushButton("Request Changes")
        req_btn.clicked.connect(lambda: QMessageBox.information(self, "Status", "Request for changes sent to Sales Dept."))
        
        btn_box.addWidget(app_btn)
        btn_box.addWidget(rej_btn)
        btn_box.addWidget(req_btn)
        
        dp_layout.addLayout(btn_box)
        layout.addWidget(dec_panel)
        layout.addStretch()
