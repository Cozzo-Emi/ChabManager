import sys
import os
import sqlite3
import subprocess
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, 
    QDateEdit, QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QDate

# ==========================================
# IMPORTACIONES DE LA NUEVA ARQUITECTURA
# ==========================================
from database.db_setup import DatabaseManager
from services.qr_service import QRService  # <-- ¡Nuestro nuevo servicio!
from ui.dialogs.qr_scanner_gui import QRScannerDialog
from ui.dialogs.export_dialog import ExportDialog
from ui.dialogs.menu_password import PasswordDialog, handle_protected_action
from ui.dialogs.print_dialog import QRPrintDialog
from ui.widgets.custom_buttons import HamburgerButton

def open_folder(path):
    if os.path.exists(path):
        if os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            subprocess.run(['xdg-open' if os.name == 'posix' else 'open', path])
    else:
        QMessageBox.warning(None, "Error", f"La carpeta {path} no existe")

class ChabManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PORTAPANEL DEL CHALECO ANTIBALAS")
        self.setGeometry(100, 100, 600, 500)
        
        self.data_dir = 'data'
        self.qr_directory = os.path.join(self.data_dir, 'qr_codes')
        self.chab_directory = os.path.join(self.data_dir, 'chab_images')
        self.db_path = os.path.join(self.data_dir, 'chab_database.db')
        
        for directory in [self.data_dir, self.qr_directory, self.chab_directory]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        self.db_manager = DatabaseManager(db_name=self.db_path)
        self.current_lot = self.db_manager.get_current_lot()
        
        # --- Instanciar el servicio de QR ---
        self.qr_service = QRService(self.qr_directory)
        
        self.lote_label = None
        self.stats_label = None
        self.modelo_input = None
        self.serie_input = None
        self.talle_combo = None
        self.genero_combo = None
        self.fecha_edit = None
        self.material_combo = None
        
        self.init_ui()
        self.setup_hamburger_menu()
        
        self.lote_label.setText(f"Lote actual: {self.current_lot:05d}")
        self.update_stats()

    def setup_hamburger_menu(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)
        
        hamburger_button = HamburgerButton()
        menu = QMenu(hamburger_button)
        
        export_action = menu.addAction('Exportar')
        export_action.triggered.connect(lambda: handle_protected_action(self, self.open_export_dialog))
        
        qr_action = menu.addAction('Códigos QR')
        qr_action.triggered.connect(lambda: handle_protected_action(
            self, lambda: open_folder(self.qr_directory)
        ))
        
        chab_action = menu.addAction('CHABS')
        chab_action.triggered.connect(lambda: handle_protected_action(
            self, lambda: open_folder(self.chab_directory)
        ))
        
        menu.addSeparator()
        
        exit_action = menu.addAction('Salir')
        exit_action.triggered.connect(self.close)
        
        hamburger_button.setMenu(menu)
        menubar.setCornerWidget(hamburger_button, Qt.Corner.TopLeftCorner)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        title = QLabel("PORTAPANEL DEL CHALECO ANTIBALAS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        self.lote_label = QLabel("Lote actual: 00000")
        layout.addWidget(self.lote_label)
        
        form_layout = QVBoxLayout()
        
        modelo_layout = QHBoxLayout()
        modelo_label = QLabel("Modelo:")
        self.modelo_input = QLineEdit()
        modelo_layout.addWidget(modelo_label)
        modelo_layout.addWidget(self.modelo_input)
        form_layout.addLayout(modelo_layout)
        
        serie_layout = QHBoxLayout()
        serie_label = QLabel("Serie Nro:")
        self.serie_input = QLineEdit()
        serie_layout.addWidget(serie_label)
        serie_layout.addWidget(self.serie_input)
        form_layout.addLayout(serie_layout)
        
        talle_layout = QHBoxLayout()
        talle_label = QLabel("Talle:")
        self.talle_combo = QComboBox()
        self.talle_combo.addItems(['XS', 'S', 'M', 'L', 'XL', 'XXL'])
        talle_layout.addWidget(talle_label)
        talle_layout.addWidget(self.talle_combo)
        form_layout.addLayout(talle_layout)
        
        genero_layout = QHBoxLayout()
        genero_label = QLabel("Género:")
        self.genero_combo = QComboBox()
        self.genero_combo.addItems(['MASC', 'FEM'])
        genero_layout.addWidget(genero_label)
        genero_layout.addWidget(self.genero_combo)
        form_layout.addLayout(genero_layout)
        
        fecha_layout = QHBoxLayout()
        fecha_label = QLabel("Fecha de Fabricación:")
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        fecha_layout.addWidget(fecha_label)
        fecha_layout.addWidget(self.fecha_edit)
        form_layout.addLayout(fecha_layout)
        
        material_layout = QHBoxLayout()
        material_label = QLabel("Material:")
        self.material_combo = QComboBox()
        self.material_combo.addItems(['KEVLAR', 'POLIETILENO', 'ARAMIDA', 'COMPUESTO HÍBRIDO', 'OTRO'])
        material_layout.addWidget(material_label)
        material_layout.addWidget(self.material_combo)
        form_layout.addLayout(material_layout)
        
        layout.addLayout(form_layout)
        
        scanner_button = QPushButton("Abrir Scanner QR")
        scanner_button.clicked.connect(self.open_scanner)
        layout.addWidget(scanner_button)
        
        self.register_button = QPushButton("Registrar CHAB")
        self.register_button.clicked.connect(self.register_chab)
        layout.addWidget(self.register_button)
        
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)

    def open_export_dialog(self):
        dialog = ExportDialog(self.db_manager, self)
        dialog.exec()
    
    def open_scanner(self):
        scanner_dialog = QRScannerDialog(self)
        scanner_dialog.exec()
    
    def update_stats(self):
        count = self.db_manager.get_lot_count(self.current_lot)
        self.stats_label.setText(f"CHABs registrados en lote actual: {count}/1300")

    def register_chab(self):
        modelo = self.modelo_input.text()
        serie = self.serie_input.text()
        talle = self.talle_combo.currentText()
        genero = self.genero_combo.currentText()
        fecha_fabricacion = self.fecha_edit.date().toPyDate()
        material = self.material_combo.currentText()
        
        if not all([modelo, serie]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        try:
            chab_data = {
                'modelo': modelo,
                'serie_nro': serie,
                'talle': talle,
                'genero': genero,
                'fecha_fabricacion': fecha_fabricacion,
                'material': material
            }
            
            # --- Aquí usamos nuestro nuevo servicio en lugar del método interno ---
            qr_code, qr_path = self.qr_service.generate_qr(chab_data, self.current_lot)
            
            data = (
                modelo, serie, self.current_lot, talle, genero,
                fecha_fabricacion, material, qr_code, qr_path
            )
            self.db_manager.insert_chab(data)
            
            print_data = {
                'modelo': modelo,
                'serie': serie,
                'lote': self.current_lot,
                'talle': talle,
                'genero': genero,
                'material': material,
                'fecha_fab': fecha_fabricacion.strftime('%Y-%m-%d')
            }
            
            print_dialog = QRPrintDialog(qr_path, print_data, self)
            print_dialog.exec()
            
            QMessageBox.information(
                self, "Éxito", f"CHAB registrado correctamente\nCódigo QR guardado en: {qr_path}"
            )
            
            self.modelo_input.clear()
            self.serie_input.clear()
            self.update_stats()
            
            count = self.db_manager.get_lot_count(self.current_lot)
            if count >= 1300:
                self.db_manager.complete_lot(self.current_lot)
                self.current_lot += 1
                self.lote_label.setText(f"Lote actual: {self.current_lot:05d}")
                QMessageBox.information(
                    self, "Lote Completado",
                    f"El lote {self.current_lot-1:05d} ha sido completado. Iniciando lote {self.current_lot:05d}"
                )
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "El número de serie ya existe en la base de datos")