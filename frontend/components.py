from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

class StatCard(QFrame):
    def __init__(self, title, value, color="#1e3a8a", icon_name=None):
        super().__init__()
        self.setObjectName("StatCard")
        self.setStyleSheet(f"""
            #StatCard {{
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e5e7eb;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #6b7280; border: none;")
        layout.addWidget(self.title_label)
        
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {color}; margin-top: 5px; border: none;")
        layout.addWidget(self.value_label)
        
        self.trend_label = QLabel("↑ 12% vs last month") # Default trend
        self.trend_label.setStyleSheet("font-size: 12px; color: #10b981; margin-top: 5px; border: none;")
        layout.addWidget(self.trend_label)

    def update_value(self, value):
        self.value_label.setText(str(value))

class ActionCard(QPushButton):
    def __init__(self, title, description, bg_color="#f8fafc", text_color="#1e3a8a"):
        super().__init__()
        self.setObjectName("ActionCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(110)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {text_color}; background: transparent; border: none;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 13px; color: #64748b; background: transparent; border: none;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        self.setStyleSheet(f"""
            #ActionCard {{
                background-color: {bg_color};
                border-radius: 14px;
                border: 1px solid #e2e8f0;
                text-align: left;
            }}
            #ActionCard:hover {{
                background-color: white;
                border: 2px solid {text_color};
            }}
        """)

class SidebarButton(QPushButton):
    def __init__(self, text, icon_name=None, active=False):
        super().__init__(text)
        self.setCheckable(True)
        self.setChecked(active)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(45)
        self.update_style()
        self.clicked.connect(self.update_style)

    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: white;
                    border-radius: 8px;
                    border: none;
                    text-align: left;
                    padding-left: 15px;
                    font-weight: 600;
                    font-size: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.8);
                    border-radius: 8px;
                    border: none;
                    text-align: left;
                    padding-left: 15px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.05);
                    color: white;
                }
            """)
