import hashlib
import os

# En un sistema de producción real, nunca escribimos la contraseña acá.
# Se suele leer de una variable de entorno, por ejemplo:
# ADMIN_PASSWORD_HASH = os.getenv("APP_ADMIN_HASH", "hash_por_defecto")

_ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

def verify_admin_password(input_password: str) -> bool:
    """
    Verifica si la contraseña ingresada en texto plano 
    coincide con el hash de seguridad del sistema.
    """
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    return input_hash == _ADMIN_PASSWORD_HASH