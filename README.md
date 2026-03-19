 CHAB Manager (Trazabilidad Industrial) - Python PyQt6

Este proyecto es una aplicación de escritorio desarrollada para gestionar la trazabilidad, control de calidad y registro en la línea de producción de Chalecos Antibalas (CHAB). El sistema destaca por su evolución hacia una **arquitectura modular**, logrando un código profesional, escalable y fácil de mantener.

# Stack Tecnológico
* **Lenguaje:** Python 3
* **Interfaz Gráfica:** PyQt6
* **Base de Datos:** SQLite3
* **Librerías Clave:** OpenCV (`opencv-python`), Pandas, PyZbar, qrcode

#Características y Arquitectura
Para garantizar un rendimiento óptimo, seguridad y un código estructurado, implementé:
* **Validación Multicámara en Tiempo Real:** Integración con OpenCV para procesar streams de video asíncronos, permitiendo escanear códigos QR con varias cámaras en simultáneo y capturar evidencia fotográfica.
* **Estructura por Capas:El código está organizado en `core` (seguridad), `database` (persistencia), `services` (lógica de negocio) y `ui` (interfaz gráfica interactiva), separando estrictamente las responsabilidades.
* **Gestión de Reportes y Trazabilidad:** Generación dinámica de códigos QR para impresión de etiquetas y exportación estructurada de la base de datos a formatos `.csv` y `.xlsx` filtrables por lote.
* **Seguridad:** Los módulos sensibles de la aplicación están protegidos mediante validación de credenciales con encriptación hash (SHA-256).

#Sobre el Autor
Soy estudiante avanzado de desarrollo de software con base técnica en **Soporte IT**. Cuento con la certificación de **Soporte de TI de Google** y experiencia coordinando talleres de tecnología.

---
*Explora mi código y conectemos en [LinkedIn](https://www.linkedin.com/in/emi-cozzolino/).*
