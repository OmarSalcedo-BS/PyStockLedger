
# PyStockLedger

Dashboard de stock de inventarios y manejo de datos. Este proyecto está pensado como un ejercicio de estudio, con enfoque en ser escalable y fácil de evolucionar a medida que se agreguen módulos y funcionalidades.

Sistema de gestión de inventarios con arquitectura de datos robusta.


## 🛠️ Arquitectura de Persistencia
Hemos implementado una capa de **Sanitización de Datos** para garantizar la integridad del sistema:

1. **Storage Layer (`storage.py`)**: Gestiona la lectura y escritura física de archivos.
2. **Standardization Layer (`data_handler.py`)**: Utiliza **Pandas** para inyectar valores por defecto (SKU: N/A, IVA: 0.19) y validar tipos numéricos.
3. **Core Logic (`inventory.py`)**: Recibe datos limpios y listos para la operación del negocio.


## Estructura del proyecto


## Requisitos
- Python 3.12
- pip
- Git

## Instalación
- Clonar el repositorio
- Crear un entorno virtual con `python -m venv venv`
- Activar el entorno virtual con `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
- Instalar dependencias con `pip install -r requirements.txt`
- Ejecutar el script

## Uso
- De ser necesario aplicar un fix para el path con: $env:PYTHONPATH += ";$(Get-Location)\src"  (Windows) o export PYTHONPATH="$(pwd)/src" (Linux/Mac)
- Ejecutar el script con `python src/main.py` o desde el run


**Para contribuir:**
1. `git checkout develop`
2. `git checkout -b feature/nueva-mejora`
3. Realiza tus cambios y haz merge a `develop`.

## 📂 Estructura del Proyecto
```text
├── src/
│   ├── core/          # Lógica de negocio (Product, Inventory)
│   ├── data/          # Manejo de persistencia (Pandas Handler)
│   ├── gui/           # Interfaz gráfica (Views, Main App)
│   └── utils/         # Formateadores y validadores
├── data/              # Archivos JSON/CSV
└── main.py            # Punto de entrada