import json
import os
from src.core.product import Product

#Definición de la ruta donde se guardaran los datos
DATA_PATH = "data/inventory.json"


def save_data(products_dict: dict) -> None:
    """
    Guarda el diccionario de productos en un archivo JSON.
    """
    try:
        #Asegurar de que la carpeta data existe
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

        #Convertir los objetos Product a diccionarios antes de guardarlos
        data_to_save = {pid: p.to_dict() for pid, p in products_dict.items()}

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            print("Datos guardados exitosamente")
    
    except Exception as e:
        print(f"Error al guardar los datos: {e}")


def load_data() -> dict:
    """
    Carga los datos del archivo JSON y los convierte en un diccionario de Product.
    """
    try:
        if not os.path.exists(DATA_PATH):
            return {}

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

            #Recibir los objetos Product 
            #Se usa ** para pasar el diccionario como argumentos
            products = {(int(pid)): Product(**p) for pid, p in raw_data.items()}
            return products
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return {}