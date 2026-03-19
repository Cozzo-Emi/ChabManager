from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                        QLabel, QComboBox, QMessageBox, QFileDialog)
import pandas as pd
import os
from datetime import datetime

class ExportDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Exportar Datos")
        self.setGeometry(100, 100, 400, 200)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        lote_layout = QHBoxLayout()
        lote_label = QLabel("Lote:")
        self.lote_combo = QComboBox()
        self.load_lotes()
        lote_layout.addWidget(lote_label)
        lote_layout.addWidget(self.lote_combo)
        layout.addLayout(lote_layout)
        
        button_layout = QHBoxLayout()
        export_csv_button = QPushButton("Exportar CSV")
        export_csv_button.clicked.connect(lambda: self.export_data('csv'))
        button_layout.addWidget(export_csv_button)
        
        export_excel_button = QPushButton("Exportar Excel")
        export_excel_button.clicked.connect(lambda: self.export_data('excel'))
        button_layout.addWidget(export_excel_button)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_lotes(self):
        self.lote_combo.clear()
        self.lote_combo.addItem("Todos los lotes")
        lotes = self.db_manager.get_all_lotes()
        for lote in lotes:
            self.lote_combo.addItem(f"Lote {lote}")
    
    def export_data(self, format_type):
        try:
            selected_lote = self.lote_combo.currentText()
            lote_num = None if selected_lote == "Todos los lotes" else int(selected_lote.split()[1])
            
            data = self.db_manager.get_export_data(lote_num)
            
            if not data:
                QMessageBox.warning(self, "Error", "No hay datos para exportar")
                return
            
            df = pd.DataFrame(data)
            
            columns_order = [
                'id', 'modelo', 'serie_nro', 'lote', 'talle', 'genero',
                'fecha_fabricacion', 'material', 'validado', 'fecha_registro'
            ]
            
            existing_columns = [col for col in columns_order if col in df.columns]
            df = df[existing_columns]
            
            if 'fecha_fabricacion' in df.columns:
                df['fecha_fabricacion'] = pd.to_datetime(df['fecha_fabricacion']).dt.strftime('%Y-%m-%d')
            if 'fecha_registro' in df.columns:
                df['fecha_registro'] = pd.to_datetime(df['fecha_registro']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            file_filter = "CSV (*.csv)" if format_type == 'csv' else "Excel (*.xlsx)"
            file_ext = ".csv" if format_type == 'csv' else ".xlsx"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"chabs_export_{timestamp}{file_ext}"
            
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Guardar Archivo", default_name, file_filter
            )
            
            if filepath:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                if format_type == 'csv':
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                else:
                    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='CHABs')
                        worksheet = writer.sheets['CHABs']
                        for idx, col in enumerate(df.columns):
                            max_length = max(
                                df[col].astype(str).apply(len).max(),
                                len(str(col))
                            )
                            worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
                
                QMessageBox.information(self, "Éxito", f"Datos exportados exitosamente a {filepath}")
                self.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar datos: {str(e)}")