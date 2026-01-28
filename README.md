
# PyStockLedger

Dashboard de stock de inventarios y manejo de datos. Este proyecto está pensado como un ejercicio de estudio, con enfoque en ser escalable y fácil de evolucionar a medida que se agreguen módulos y funcionalidades.

## Estructura del proyecto

```
src/
	__init__.py        # Convierte la carpeta en un paquete
	main.py            # Punto de entrada de la aplicación
	core/              # Lógica de negocio (clases base)
		__init__.py
		product.py       # Clase Producto y herencias
		inventory.py     # Clase gestora (el "cerebro")
	data/              # Manejo de persistencia (JSON/CSV)
		__init__.py
		storage.py
	utils/             # Funciones de ayuda y validaciones
		__init__.py
		validators.py
tests/               # Pruebas unitarias
.gitignore           # Archivos que Git debe ignorar
requirements.txt     # Dependencias del proyecto
README.md            # Documentación general
```
