from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

class QRPrintDialog(QDialog):
    def __init__(self, qr_path, chab_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista previa de impresión")
        self.setGeometry(100, 100, 400, 600)
        
        layout = QVBoxLayout()
        
        # Mostrar el QR
        qr_label = QLabel()
        pixmap = QPixmap(qr_path)
        scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        qr_label.setPixmap(scaled_pixmap)
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(qr_label)
        
        # Mostrar información del CHAB
        info_label = QLabel(
            f"ID: CHAB-{chab_data['lote']:05d}-{chab_data['serie']}\n"
            f"Modelo: {chab_data['modelo']}\n"
            f"Serie: {chab_data['serie']}\n"
            f"Lote: {chab_data['lote']}\n"
            f"Talle: {chab_data['talle']}\n"
            f"Género: {chab_data['genero']}\n"
            f"Material: {chab_data['material']}\n"
            f"Fecha Fab.: {chab_data['fecha_fab']}"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Botones
        button_layout = QHBoxLayout()
        
        print_button = QPushButton("Imprimir")
        print_button.clicked.connect(self.print_qr)
        button_layout.addWidget(print_button)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.qr_path = qr_path
        self.chab_data = chab_data
        self.current_printer = None

    def print_qr(self):
        try:
            printer = QPrinter()
            if self.current_printer:
                printer = self.current_printer
            
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec() == QDialog.DialogCode.Accepted:
                self.current_printer = printer
                painter = QPainter()
                if painter.begin(printer):
                    page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
                    pixmap = QPixmap(self.qr_path)
                    scaled_qr = pixmap.scaled(int(page_rect.width() // 2), 
                                            int(page_rect.width() // 2),
                                            Qt.AspectRatioMode.KeepAspectRatio)
                    
                    qr_x = (page_rect.width() - scaled_qr.width()) // 2
                    qr_y = page_rect.height() // 4
                    painter.drawPixmap(int(qr_x), int(qr_y), scaled_qr)

                    text_rect = painter.boundingRect(
                        int(page_rect.x()) + 50,
                        int(qr_y + scaled_qr.height() + 50),
                        int(page_rect.width() - 100),
                        int(page_rect.height() - qr_y - scaled_qr.height() - 100),
                        Qt.AlignmentFlag.AlignCenter,
                        f"ID: CHAB-{self.chab_data['lote']:05d}-{self.chab_data['serie']}\n"
                        f"Modelo: {self.chab_data['modelo']}\n"
                        f"Serie: {self.chab_data['serie']}\n"
                        f"Lote: {self.chab_data['lote']}\n"
                        f"Talle: {self.chab_data['talle']}\n"
                        f"Género: {self.chab_data['genero']}\n"
                        f"Material: {self.chab_data['material']}\n"
                        f"Fecha Fab.: {self.chab_data['fecha_fab']}"
                    )
                    
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter,
                        f"ID: CHAB-{self.chab_data['lote']:05d}-{self.chab_data['serie']}\n"
                        f"Modelo: {self.chab_data['modelo']}\n"
                        f"Serie: {self.chab_data['serie']}\n"
                        f"Lote: {self.chab_data['lote']}\n"
                        f"Talle: {self.chab_data['talle']}\n"
                        f"Género: {self.chab_data['genero']}\n"
                        f"Material: {self.chab_data['material']}\n"
                        f"Fecha Fab.: {self.chab_data['fecha_fab']}"
                    )
                    
                    painter.end()
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error de impresión",
                f"Ocurrió un error al imprimir: {str(e)}"
            )