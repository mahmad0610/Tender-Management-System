from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QComboBox, 
                             QFileDialog, QMessageBox, QTabWidget, QWidget,
                             QFormLayout, QDoubleSpinBox, QSpinBox, QFrame, QDateEdit)
from PySide6.QtCore import Qt, QDate
import os

class TenderFormDialog(QDialog):
    def __init__(self, parent=None, tender_data=None):
        super().__init__(parent)
        self.tender_data = tender_data
        self.setWindowTitle("Create / Submit Tender")
        self.setMinimumSize(600, 500)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # Step 1: Basic Details
        self.step1 = QWidget()
        s1_layout = QFormLayout(self.step1)
        self.title_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.category_input = QComboBox()
        self.category_input.addItems(["Infrastructure", "IT Services", "Supply", "Consultancy"])
        self.val_input = QDoubleSpinBox()
        self.val_input.setRange(0, 1000000000)
        self.val_input.setPrefix("$ ")
        self.timeline_input = QLineEdit()
        self.timeline_input.setPlaceholderText("e.g. 90 Days")
        self.deadline_input = QDateEdit(QDate.currentDate().addDays(30))
        self.deadline_input.setCalendarPopup(True)
        
        s1_layout.addRow("Tender Title:", self.title_input)
        s1_layout.addRow("Description:", self.desc_input)
        s1_layout.addRow("Category:", self.category_input)
        s1_layout.addRow("Estimated Value:", self.val_input)
        s1_layout.addRow("Delivery Timeline:", self.timeline_input)
        s1_layout.addRow("Submission Deadline:", self.deadline_input)
        
        self.method_input = QComboBox()
        self.method_input.addItems(["Online", "Manual"])
        self.package_id_input = QLineEdit()
        self.package_id_input.setPlaceholderText("e.g. PKG-101")
        
        s1_layout.addRow("Submission Method:", self.method_input)
        s1_layout.addRow("Package ID (Ref):", self.package_id_input)
        
        # Step 2: Product / Work Details
        self.step2 = QWidget()
        s2_layout = QFormLayout(self.step2)
        self.item_name = QLineEdit()
        self.qty = QSpinBox()
        self.qty.setRange(1, 1000000)
        self.unit_cost = QDoubleSpinBox()
        self.unit_cost.setRange(0, 1000000)
        self.total_cost_label = QLabel("$ 0.00")
        self.total_cost_label.setStyleSheet("font-weight: bold; color: #1e3a8a;")
        
        s2_layout.addRow("Item/Work Name:", self.item_name)
        s2_layout.addRow("Quantity:", self.qty)
        s2_layout.addRow("Unit Cost:", self.unit_cost)
        s2_layout.addRow("Total Cost:", self.total_cost_label)
        
        self.qty.valueChanged.connect(self.update_total_cost)
        self.unit_cost.valueChanged.connect(self.update_total_cost)
        
        # Step 3: Document Upload
        self.step3 = QWidget()
        s3_layout = QVBoxLayout(self.step3)
        self.tech_doc_label = QLabel("No technical document selected")
        self.fin_doc_label = QLabel("No financial document selected")
        
        tech_btn = QPushButton("Upload Technical Document (PDF/DOC)")
        tech_btn.clicked.connect(lambda: self.upload_doc('tech'))
        fin_btn = QPushButton("Upload Financial Document (PDF/DOC)")
        fin_btn.clicked.connect(lambda: self.upload_doc('fin'))
        
        s3_layout.addWidget(tech_btn)
        s3_layout.addWidget(self.tech_doc_label)
        s3_layout.addSpacing(20)
        s3_layout.addWidget(fin_btn)
        s3_layout.addWidget(self.fin_doc_label)
        s3_layout.addStretch()
        
        # Step 4: Save / Submit
        self.step4 = QWidget()
        s4_layout = QVBoxLayout(self.step4)
        summary_label = QLabel("Review your details and select an action.\nSubmitting will lock the tender for evaluation.")
        summary_label.setStyleSheet("color: #6b7280; font-style: italic; margin-bottom: 20px;")
        s4_layout.addWidget(summary_label)
        
        btn_box = QHBoxLayout()
        self.draft_btn = QPushButton("Save as Draft")
        self.submit_btn = QPushButton("Submit Tender")
        self.submit_btn.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 10px;")
        
        self.draft_btn.clicked.connect(lambda: self.finish_tender(False))
        self.submit_btn.clicked.connect(lambda: self.finish_tender(True))
        
        btn_box.addWidget(self.draft_btn)
        btn_box.addWidget(self.submit_btn)
        s4_layout.addLayout(btn_box)
        s4_layout.addStretch()
        
        self.tabs.addTab(self.step1, "1. Basic Info")
        self.tabs.addTab(self.step2, "2. Items")
        self.tabs.addTab(self.step3, "3. Documents")
        self.tabs.addTab(self.step4, "4. Finish")
        
        main_layout.addWidget(self.tabs)
        
        self.tech_file = None
        self.fin_file = None

    def update_total_cost(self):
        total = self.qty.value() * self.unit_cost.value()
        self.total_cost_label.setText(f"$ {total:,.2f}")

    def upload_doc(self, mode):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document", "", "Documents (*.pdf *.doc *.docx)")
        if file_path:
            filename = os.path.basename(file_path)
            if mode == 'tech':
                self.tech_file = file_path
                self.tech_doc_label.setText(f"Selected: {filename}")
            else:
                self.fin_file = file_path
                self.fin_doc_label.setText(f"Selected: {filename}")

    def finish_tender(self, is_final):
        data = {
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText(),
            "category": self.category_input.currentText(),
            "estimated_cost": self.val_input.value(),
            "delivery_timeline": self.timeline_input.text(),
            "deadline": self.deadline_input.date().toPython().isoformat(),
            "item_name": self.item_name.text(),
            "quantity": self.qty.value(),
            "unit_cost": self.unit_cost.value(),
            "is_submitted": is_final,
            "submission_method": self.method_input.currentText(),
            "package_id": self.package_id_input.text()
        }
        
        if not data["title"]:
            QMessageBox.warning(self, "Missing Data", "Please provide a tender title.")
            self.tabs.setCurrentIndex(0)
            return
            
        self.accept()
        self.result_data = data

    def get_data(self):
        return self.result_data
