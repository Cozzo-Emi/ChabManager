from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
from pyzbar.pyzbar import decode
import os
from datetime import datetime

# IMPORTACIÓN CORREGIDA A LA NUEVA ARQUITECTURA
from database.db_setup import DatabaseManager

class MultiCameraManager:
    def __init__(self):
        self.cameras = []
        self.active_cameras = []
        self.detect_cameras()
    
    def detect_cameras(self):
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                break
            self.cameras.append(index)
            cap.release()
            index += 1
    
    def get_camera_count(self):
        return len(self.cameras)

class QRScannerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scanner QR Multicámara")
        self.setGeometry(100, 100, 1200, 800)
        
        # Asegurar ruta correcta
        self.data_dir = 'data'
        self.images_dir = os.path.join(self.data_dir, 'chab_images')
        self.db_path = os.path.join(self.data_dir, 'chab_database.db')
        
        self.db_manager = DatabaseManager(db_name=self.db_path)
        self.camera_manager = MultiCameraManager()
        self.cameras = []
        self.timers = []
        self.image_labels = []
        self.qr_detected = False
        self.active_camera_index = None
        self.processing_complete = False
        
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            
        self.init_ui()
        self.init_cameras()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        camera_grid = QGridLayout()
        num_cameras = self.camera_manager.get_camera_count()
        
        cols = min(2, num_cameras)
        rows = (num_cameras + 1) // 2
        
        for i in range(num_cameras):
            label = QLabel()
            label.setMinimumSize(400, 300)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("border: 2px solid gray;")
            self.image_labels.append(label)
            row = i // cols
            col = i % cols
            camera_grid.addWidget(label, row, col)
        
        main_layout.addLayout(camera_grid)
        
        self.status_label = QLabel("Esperando QR en cualquier cámara...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close_scanner)
        main_layout.addWidget(close_button)
        
        self.setLayout(main_layout)
    
    def init_cameras(self):
        num_cameras = self.camera_manager.get_camera_count()
        
        if num_cameras == 0:
            QMessageBox.critical(self, "Error", "No se detectaron cámaras")
            # Se usa un timer para cerrar después de que la UI cargue
            QTimer.singleShot(100, self.close)
            return
            
        for i in range(num_cameras):
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                self.cameras.append(camera)
                timer = QTimer()
                timer.timeout.connect(lambda idx=i: self.update_frame(idx))
                timer.start(30)
                self.timers.append(timer)
            
        self.status_label.setText(f"Detectadas {len(self.cameras)} cámaras activas")

    def reset_scanner(self):
        self.qr_detected = False
        self.active_camera_index = None
        self.processing_complete = False
        
        for label in self.image_labels:
            label.setStyleSheet("border: 2px solid gray;")
        
        self.status_label.setText("Esperando nuevo QR en cualquier cámara...")
        self.status_label.setStyleSheet("color: black")
    
    def update_frame(self, camera_index):
        if self.processing_complete:
            self.reset_scanner()
            
        camera = self.cameras[camera_index]
        ret, frame = camera.read()
        
        if ret:
            if not self.qr_detected:
                decoded_objects = decode(frame)
                for obj in decoded_objects:
                    if self.process_qr(obj, frame, camera_index):
                        break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.image_labels[camera_index].size(), 
                Qt.AspectRatioMode.KeepAspectRatio
            )
            
            if camera_index == self.active_camera_index and self.qr_detected:
                self.image_labels[camera_index].setStyleSheet("border: 3px solid green;")
            else:
                self.image_labels[camera_index].setStyleSheet("border: 2px solid gray;")
                
            self.image_labels[camera_index].setPixmap(scaled_pixmap)
    
    def process_qr(self, qr_object, frame, camera_index):
        if self.qr_detected:
            return False
            
        try:
            qr_data = eval(qr_object.data.decode('utf-8'))
            serie_nro = qr_data.get('serie')
            lote = qr_data.get('lote')
            
            chab_info = self.db_manager.get_chab_by_qr_data(serie_nro, lote)
            
            if chab_info:
                if chab_info['validado']:
                    self.status_label.setText(f"¡QR ya validado! (Cámara {camera_index + 1})")
                    self.status_label.setStyleSheet("color: orange")
                    self.processing_complete = True
                    return False
                
                self.qr_detected = True
                self.active_camera_index = camera_index
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"chab_{chab_info['id']}_{timestamp}.jpg"
                
                # RUTA CORREGIDA A LA NUEVA ARQUITECTURA
                image_path = os.path.join(self.images_dir, image_filename)
                
                info_text = [
                    f"ID: CHAB-{lote:05d}-{serie_nro}",
                    f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    f"Cámara: {camera_index + 1}"
                ]
                
                y_position = 30
                for text in info_text:
                    cv2.putText(frame, text, (10, y_position),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_position += 30
                
                cv2.imwrite(image_path, frame)
                
                if self.db_manager.save_chab_validation(serie_nro, lote, image_path):
                    self.status_label.setText(
                        f"¡QR Válido! CHAB ID: {chab_info['id']} (Cámara {camera_index + 1})"
                    )
                    self.status_label.setStyleSheet("color: green")
                    
                    QMessageBox.information(
                        self, "Éxito", f"Validación guardada exitosamente\nImagen guardada en: {image_path}"
                    )
                    
                    self.processing_complete = True
                    return True
                else:
                    self.status_label.setText(f"Error al guardar la validación (Cámara {camera_index + 1})")
                    self.status_label.setStyleSheet("color: red")
                    self.processing_complete = True
            
            return False
                
        except Exception as e:
            self.status_label.setText(f"Error en cámara {camera_index + 1}: {str(e)}")
            self.status_label.setStyleSheet("color: red")
            self.processing_complete = True
            return False
    
    def close_scanner(self):
        for timer in self.timers:
            timer.stop()
        for camera in self.cameras:
            if camera is not None:
                camera.release()
        self.close()
    
    def closeEvent(self, event):
        self.close_scanner()
        event.accept()