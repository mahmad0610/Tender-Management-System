import sys
import os

# Ensure we're running under Python 3.6+ because this codebase uses f-strings
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit(
        "Tender UI requires Python 3.6+ — run with `python3 -m frontend.main` or activate a Python 3 venv."
    )
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QStackedWidget, QFrame, QMessageBox, QComboBox,
                             QScrollArea, QGridLayout, QTextEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFormLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QFont

# Internal Imports
from .components import SidebarButton, StatCard, ActionCard
from .admin_dashboard import AdminDashboard
from .client_portal import ClientPortal
from .vendor_portal import VendorPortal
from .finance_dashboard import FinanceDashboard
from .sales_dashboard import TechnicalDashboard

# Specialized Views
from .tender_views import TenderListView
from .evaluation_views import TechnicalEvaluationView, FinancialEvaluationView, ClientApprovalView
from .lifecycle_views import OrderGenerationView, ContractManagementView, DeliveryMilestoneView, BillingInvoiceView, PaymentManagementView
from .admin_views import ReportsAnalyticsView, AuditLogsView, AdminSettingsView

API_URL = "http://localhost:8000"

GLOBAL_STYLE = """
    QMainWindow { 
        background-color: #f8fafc; 
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
    }
    #Sidebar { 
        background-color: #0f172a; 
        border: none; 
    }
    #PrimaryButton { 
        background-color: #2563eb; 
        color: white; 
        border-radius: 10px; 
        font-weight: 700; 
        padding: 14px; 
        font-size: 15px;
        border: none;
    }
    #PrimaryButton:hover { 
        background-color: #1d4ed8; 
    }
    #Input { 
        background-color: #ffffff; 
        border: 1.5px solid #e2e8f0; 
        border-radius: 10px; 
        padding: 12px 15px; 
        color: #1e293b; 
        font-size: 14px;
    }
    #Input:focus {
        border-color: #3b82f6;
    }
    QTableWidget {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        gridline-color: #f1f5f9;
        color: #1e293b;
    }
    QTableWidget::item {
        padding: 8px;
        color: #1e293b;
        border-bottom: 1px solid #f1f5f9;
    }
    QTableWidget::item:selected {
        background-color: #dbeafe;
        color: #1e3a8a;
    }
    QHeaderView::section {
        background-color: #f8fafc;
        color: #475569;
        padding: 10px;
        border: none;
        border-bottom: 2px solid #e2e8f0;
        font-weight: 600;
        font-size: 13px;
    }
"""

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setMinimumSize(1000, 650)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Panel (Branding) - Fixed width to ensure it doesn't take over
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #1e3a8a;")
        left_panel.setFixedWidth(400) # Fixed width for sidebar feel
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setAlignment(Qt.AlignCenter)
        
        logo_label = QLabel("TM")
        logo_label.setFixedSize(80, 80)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: 800; 
            color: white; 
            background-color: #2563eb; 
            border-radius: 20px;
        """)
        left_layout.addWidget(logo_label, 0, Qt.AlignCenter)
        
        title = QLabel("Tender Management System")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: white; margin-top: 30px;")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        subtitle = QLabel("The ultimate procurement ecosystem for enterprise growth.")
        subtitle.setStyleSheet("font-size: 16px; color: #94a3b8; margin-top: 15px;")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(subtitle)
        
        main_layout.addWidget(left_panel)
                                                                                 
        # Right Panel (Login Form)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter) # Center the form vertically/horizontally
        
        form_container = QWidget()
        form_container.setFixedWidth(400)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        welcome = QLabel("User Login")
        welcome.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a; margin-bottom: 5px;")
        form_layout.addWidget(welcome)
        
        instruction = QLabel("Enter your credentials to access your dashboard.")
        instruction.setStyleSheet("color: #64748b; font-size: 14px; margin-bottom: 35px;")
        form_layout.addWidget(instruction)

        u_label = QLabel("Username or Email")
        u_label.setStyleSheet("font-weight: 700; color: #334155; margin-bottom: 8px; font-size: 13px;")
        form_layout.addWidget(u_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g. admin")
        self.username_input.setObjectName("Input")
        self.username_input.setFixedHeight(50)
        form_layout.addWidget(self.username_input)

        # Add quick demo login buttons for each role
        demo_users = [
            ("Admin", "admin", "admin"),
            ("Technical", "technical", "technical"),
            ("Client", "client", "client"),
            ("Vendor", "vendor", "vendor"),
            ("Finance", "finance", "finance"),
        ]
        demo_btn_layout = QHBoxLayout()
        for label, uname, pwd in demo_users:
            btn = QPushButton(label)
            btn.setStyleSheet("font-size: 12px; padding: 5px; border-radius: 6px; background: #e0e7ef; color: #1e293b; border: none;")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, u=uname, p=pwd: self.fill_demo_login(u, p))
            demo_btn_layout.addWidget(btn)
        form_layout.addLayout(demo_btn_layout)

        p_label = QLabel("Password")
        p_label.setStyleSheet("font-weight: 700; color: #334155; margin-bottom: 8px; margin-top: 20px; font-size: 13px;")
        form_layout.addWidget(p_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("Input")
        self.password_input.setFixedHeight(50)
        form_layout.addWidget(self.password_input)
        
        form_layout.addSpacing(30)
        
        self.login_button = QPushButton("Sign In to Dashboard")
        self.login_button.setObjectName("PrimaryButton")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setFixedHeight(55)
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)
        
        right_layout.addWidget(form_container)
        main_layout.addWidget(right_panel)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})
            if response.status_code == 200:
                self.on_login_success(response.json())
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Server not reachable: {e}")

class DashboardWrapper(QWidget):
    def __init__(self, user_data, logout_callback):
        super().__init__()
        self.user_data = user_data
        self.logout_callback = logout_callback
        self.current_view_name = "Dashboard"
        self.views = {}
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)

        brand = QLabel("Tender Tracking")
        brand.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin: 0 30px 40px 30px;")
        sidebar_layout.addWidget(brand)

        self.nav_group = []
        menu_items = self.get_menu_items(self.user_data['role'])
        
        for item in menu_items:
            btn = SidebarButton(item)
            btn.clicked.connect(lambda checked, n=item: self.navigate_to(n))
            sidebar_layout.addWidget(btn)
            self.nav_group.append(btn)
            
        sidebar_layout.addStretch()
        
        # Sidebar Logout
        self.logout_btn = SidebarButton("Sign Out")
        self.logout_btn.clicked.connect(self.logout_callback)
        sidebar_layout.addWidget(self.logout_btn)

        layout.addWidget(self.sidebar)

        # Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #e5e7eb;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        self.header_title = QLabel("Dashboard")
        self.header_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; border: none;")
        header_layout.addWidget(self.header_title)
        
        header_layout.addStretch()
        
        user_info = QLabel(f"{self.user_data['full_name'] or self.user_data['username']} • {self.user_data['role'].capitalize()}")
        user_info.setStyleSheet("color: #6b7280; font-size: 14px; border: none; margin-right: 15px;")
        header_layout.addWidget(user_info)

        self.header_logout_btn = QPushButton("Log Out")
        self.header_logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                color: #dc2626;
                padding: 6px 15px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #fecaca;
            }
            QPushButton:hover {
                background-color: #fecaca;
            }
        """)
        self.header_logout_btn.setCursor(Qt.PointingHandCursor)
        self.header_logout_btn.clicked.connect(self.logout_callback)
        header_layout.addWidget(self.header_logout_btn)
        
        content_layout.addWidget(header)
        
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        layout.addWidget(content_container)
        self.navigate_to("Dashboard")

    def get_menu_items(self, role):
        role_menus = {
            "admin": ["User Management", "Audit Logs", "Admin Settings"],
            "technical": ["Tender List", "Technical Evaluation", "Reports"],
            "finance": ["Financial Evaluation", "Invoicing", "Payment Verification", "Ledger"],
            "client": ["Post Tender", "Tender List", "Client Approval", "Payment Recording"],
            "vendor": ["Tender List", "My Submissions", "Delivery Tracking", "Vendor Payments"]
        }
        return ["Dashboard"] + role_menus.get(role, []) + ["Settings"]

    def navigate_to(self, name):
        for btn in self.nav_group:
            btn.setChecked(btn.text() == name)
            btn.update_style()
        
        self.header_title.setText(name)
        self.current_view_name = name
        
        if name not in self.views:
            view = self.create_view(name)
            if view:
                self.views[name] = view
                self.content_stack.addWidget(view)
        
        if name in self.views:
            self.content_stack.setCurrentWidget(self.views[name])

    def create_view(self, name):
        role = self.user_data['role']
        
        if name == "Dashboard":
            if role == 'admin': return AdminDashboard(self.user_data)
            elif role == 'technical': return TechnicalDashboard(self.user_data)
            elif role == 'client': return ClientPortal(self.user_data)
            elif role == 'finance': return FinanceDashboard(self.user_data)
            elif role == 'vendor': return VendorPortal(self.user_data)
        
        if name == "Tender List": return TenderListView(self.user_data)
        if name == "Post Tender": return TenderListView(self.user_data)
        
        if name == "Technical Evaluation": return TechnicalEvaluationView(self.user_data)
        if name == "Financial Evaluation": return FinancialEvaluationView(self.user_data)
        if name == "Client Approval": return ClientApprovalView(self.user_data)
        
        if name == "Invoicing": return BillingInvoiceView(self.user_data, is_finance=True)
        if name == "Payment Verification": return PaymentManagementView(self.user_data, is_recording=False)
        if name == "Payment Recording": return PaymentManagementView(self.user_data, is_recording=True)
        
        if name == "Delivery Tracking": return DeliveryMilestoneView(self.user_data)
        if name == "Vendor Payments": return PaymentManagementView(self.user_data, is_recording=False)
        if name == "My Submissions": return DeliveryMilestoneView(self.user_data)
        
        if name == "Audit Logs": return AuditLogsView(self.user_data)
        if name == "Admin Settings": return AdminSettingsView(self.user_data)
        if name == "Reports": return ReportsAnalyticsView(self.user_data)
        if name == "Ledger": return ReportsAnalyticsView(self.user_data)
        if name == "Settings": return AdminSettingsView(self.user_data)
        if name == "User Management": return AdminDashboard(self.user_data)

        return QLabel(f"Functional Module for {name} is ready.")

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tender Management - Procurement System")
        self.resize(1280, 850)
        self.setStyleSheet(GLOBAL_STYLE)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_window = LoginWindow(self.show_dashboard)
        self.stacked_widget.addWidget(self.login_window)

    def show_dashboard(self, user_data):
        self.dashboard_wrapper = DashboardWrapper(user_data, self.logout)
        self.stacked_widget.addWidget(self.dashboard_wrapper)
        self.stacked_widget.setCurrentWidget(self.dashboard_wrapper)

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec_())
