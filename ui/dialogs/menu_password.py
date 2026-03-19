from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)

# IMPORTACIÓN DE NUESTRA NUEVA CAPA CORE
from core.security import verify_admin_password

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verificación")
        self.setGeometry(300, 300, 250, 100)
        
        layout = QVBoxLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password_input)
        
        verify_button = QPushButton("Verificar")
        verify_button.clicked.connect(self.verify_password)
        layout.addWidget(verify_button)
        
        self.setLayout(layout)
    
    def verify_password(self):
        # Delegamos la responsabilidad de la seguridad a la capa Core
        if verify_admin_password(self.password_input.text()):
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Contraseña incorrecta")
            self.password_input.clear()

def handle_protected_action(parent, action):
    dialog = PasswordDialog(parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        action()