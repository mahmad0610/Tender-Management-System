from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QScrollArea, QFrame)
from PySide6.QtCore import Qt
from .components import StatCard, ActionCard
import requests

API_URL = "http://localhost:8000"

class TechnicalDashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Stats
        stats_layout = QHBoxLayout()
        self.pending_eval = StatCard("Pending Evaluations", "0", "#2563eb")
        self.completed_eval = StatCard("Completed Reviews", "0", "#059669")
        self.avg_score = StatCard("Avg. Tech Score", "0", "#d97706")
        
        stats_layout.addWidget(self.pending_eval)
        stats_layout.addWidget(self.completed_eval)
        stats_layout.addWidget(self.avg_score)
        layout.addLayout(stats_layout)

        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(ActionCard("Technical Review", "Scores & Remarks", "#eff6ff", "#2563eb"))
        actions_layout.addWidget(ActionCard("Margin Analysis", "Internal feasibility", "#f0fdf4", "#059669"))
        actions_layout.addWidget(ActionCard("Export Reports", "PDF summaries", "#fffbeb", "#d97706"))
        layout.addLayout(actions_layout)

        # Table
        table_label = QLabel("Queue: Awaiting Technical Score")
        table_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; margin-top: 20px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ref", "Project", "Client ID", "Deadline"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        layout.addStretch()
        self.refresh_data()

    def refresh_data(self):
        try:
            res = requests.get(f"{API_URL}/tenders/")
            if res.status_code == 200:
                tenders = res.json()
                # Tenders awaiting tech review
                pending = [t for t in tenders if t['status'] in ['open', 'submitted']]
                
                self.table.setRowCount(len(pending))
                for i, t in enumerate(pending):
                    self.table.setItem(i, 0, QTableWidgetItem(t['tender_id']))
                    self.table.setItem(i, 1, QTableWidgetItem(t['title']))
                    self.table.setItem(i, 2, QTableWidgetItem(str(t.get('client_id', 'N/A'))))
                    self.table.setItem(i, 3, QTableWidgetItem(t['deadline'][:16].replace('T', ' ')))
                
                self.pending_eval.update_value(str(len(pending)))
                
                # Fetch proposals for scores and completed reviews
                prop_res = requests.get(f"{API_URL}/proposals/")
                if prop_res.status_code == 200:
                    proposals = prop_res.json()
                    scored_proposals = [p for p in proposals if p['technical_score'] > 0]
                    avg_score = sum(p['technical_score'] for p in scored_proposals) / len(scored_proposals) if scored_proposals else 0
                    self.avg_score.update_value(f"{avg_score:.1f}/100")
                    self.completed_eval.update_value(str(len(scored_proposals)))
        except Exception as e:
            print(f"Error refreshing technical dashboard: {e}")
