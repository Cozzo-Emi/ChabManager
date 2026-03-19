import sys
from PyQt6.QtWidgets import QApplication

# Importamos la ventana principal desde nuestra nueva capa de interfaz de usuario (UI)
from ui.main_window import ChabManagerApp

def main():
    """Punto de entrada principal de la aplicación."""
    
    # Inicializar la aplicación de Qt
    app = QApplication(sys.argv)
    
    # Crear y mostrar la ventana principal
    window = ChabManagerApp()
    window.show()
    
    # Ejecutar el bucle de eventos y salir limpiamente
    sys.exit(app.exec())

if __name__ == '__main__':
    main()