import os
import qrcode
from io import BytesIO

class QRService:
    def __init__(self, qr_directory):
        self.qr_directory = qr_directory
        
        # Nos aseguramos de que el directorio exista desde el servicio
        if not os.path.exists(self.qr_directory):
            os.makedirs(self.qr_directory)

    def generate_qr(self, chab_data, current_lot):
        """Genera el código QR, lo guarda en disco y retorna los bytes y la ruta."""
        
        unique_id = f"CHAB-{current_lot:05d}-{chab_data['serie_nro']}"
        
        qr_data = {
            'id': unique_id,
            'modelo': chab_data['modelo'],
            'serie': chab_data['serie_nro'],
            'lote': current_lot,
            'talle': chab_data['talle'],
            'genero': chab_data['genero'],
            'material': chab_data['material'],
            'fecha_fab': chab_data['fecha_fabricacion'].strftime('%Y-%m-%d')
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(self.qr_directory, f"{unique_id}.png")
        qr_image.save(qr_path)
        
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_bytes = buffer.getvalue()
        
        return qr_bytes, qr_path