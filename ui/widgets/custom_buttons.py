from PyQt6.QtWidgets import QToolButton

class HamburgerButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setText('☰') 
        self.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
                font-size: 20px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #786E6466;
            }
            QToolButton::menu-indicator { 
                image: none;
            }
        """)