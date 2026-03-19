import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name='data/chab_database.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        # Asegurar que el directorio exista antes de conectar
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Crear tabla de chabs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chabs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modelo TEXT NOT NULL,
                    serie_nro TEXT NOT NULL UNIQUE,
                    lote INTEGER NOT NULL,
                    talle TEXT NOT NULL,
                    genero TEXT NOT NULL,
                    fecha_fabricacion DATE NOT NULL,
                    material TEXT NOT NULL,
                    qr_code BLOB NOT NULL,
                    qr_path TEXT NOT NULL,
                    chab_image_blob BLOB,
                    chab_image_path TEXT,
                    validado BOOLEAN DEFAULT 0,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear tabla de lotes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lotes (
                    lote INTEGER PRIMARY KEY,
                    fecha_inicio TIMESTAMP,
                    completado BOOLEAN DEFAULT 0
                )
            ''')
            
            # Crear tabla de validaciones (faltaba crearla en el init original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chab_id INTEGER,
                    imagen_path TEXT,
                    fecha_validacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(chab_id) REFERENCES chabs(id)
                )
            ''')
            
            conn.commit()
    
    def get_current_lot(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lote FROM lotes 
                WHERE completado = 0 
                ORDER BY lote DESC LIMIT 1
            ''')
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                cursor.execute('''
                    INSERT INTO lotes (lote, fecha_inicio) 
                    VALUES (1, CURRENT_TIMESTAMP)
                ''')
                conn.commit()
                return 1
    
    def complete_lot(self, lot_number):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE lotes 
                SET completado = 1 
                WHERE lote = ?
            ''', (lot_number,))
            
            cursor.execute('''
                INSERT INTO lotes (lote, fecha_inicio) 
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (lot_number + 1,))
            
            conn.commit()
    
    def get_lot_count(self, lot_number):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM chabs 
                WHERE lote = ?
            ''', (lot_number,))
            return cursor.fetchone()[0]
    
    def insert_chab(self, data):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chabs (
                    modelo, serie_nro, lote, talle, genero, 
                    fecha_fabricacion, material, qr_code, qr_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()
            return cursor.lastrowid
            
    def get_all_lotes(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT lote FROM chabs ORDER BY lote')
            return [row[0] for row in cursor.fetchall()]

    def is_chab_validated(self, serie_nro, lote):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT validado 
                FROM chabs 
                WHERE serie_nro = ? AND lote = ?
            ''', (serie_nro, lote))
            result = cursor.fetchone()
            return result[0] if result else False

    def save_chab_validation(self, serie_nro, lote, image_path):
        try:
            with open(image_path, 'rb') as image_file:
                image_blob = image_file.read()
            
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE chabs 
                    SET chab_image_blob = ?, 
                        chab_image_path = ?,
                        validado = 1 
                    WHERE serie_nro = ? AND lote = ?
                ''', (image_blob, image_path, serie_nro, lote))
                
                # También registramos en la tabla de validaciones
                chab_info = self.get_chab_by_qr_data(serie_nro, lote)
                if chab_info:
                    cursor.execute('''
                        INSERT INTO validaciones (chab_id, imagen_path)
                        VALUES (?, ?)
                    ''', (chab_info['id'], image_path))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al guardar la validación: {str(e)}")
            return False

    def get_chab_by_qr_data(self, serie_nro, lote):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, validado 
                FROM chabs 
                WHERE serie_nro = ? AND lote = ?
            ''', (serie_nro, lote))
            result = cursor.fetchone()
            if result:
                return {'id': result[0], 'validado': result[1]}
            return None
    
    def get_chab_image(self, serie_nro, lote):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT chab_image_blob, chab_image_path
                FROM chabs 
                WHERE serie_nro = ? AND lote = ?
            ''', (serie_nro, lote))
            return cursor.fetchone()
    
    def get_export_data(self, lote=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    id, modelo, serie_nro, lote, talle, genero,
                    fecha_fabricacion, material, validado, fecha_registro
                FROM chabs
            '''
            
            params = []
            if lote is not None:
                query += ' WHERE lote = ?'
                params.append(lote)
            
            query += ' ORDER BY fecha_registro'
            
            cursor.execute(query, params)
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result