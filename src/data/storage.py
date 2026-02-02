import json
import os
from src.core.product import Product
from src.core.transaction import Transaction

# Definición de la ruta donde se guardaran los datos
DATA_PATH = "data/inventory.json"
TRANS_PATH = "data/transactions.json"


def save_data(products_dict: dict, transactions_list: list) -> None:
    """
    Guarda Productos e historial en sus respectivos archivos.
    """
    try:
        # Asegurar de que la carpeta data existe
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

        # Convertir los objetos Product a diccionarios antes de guardarlos
        data_to_save = {pid: p.to_dict() for pid, p in products_dict.items()}
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            

       # Serializar las transacciones (lista de objetos -> lista de dicts)
        history_to_save = [t.to_dict() for t in transactions_list]
        with open(TRANS_PATH, "w", encoding="utf-8") as f:
            json.dump(history_to_save, f, indent=4, ensure_ascii=False)

            print("Datos y movimientos  guardados exitosamente")
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

            # Recibir los objetos Product
            # Se usa ** para pasar el diccionario como argumentos
            products = {(int(pid)): Product(**p) for pid, p in raw_data.items()}
            return products
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return {}

def load_transactions() -> list:
    """Carga el historial desde el archivo JSON."""
    if not os.path.exists(TRANS_PATH):
        return []
    try:
        with open(TRANS_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            #Forzaremos que el producto_id sea int
            history = []
            for t in raw_data:
                t['product_id'] = int(t['product_id'])
                history.append(Transaction(**t))
            return history
    except Exception as e:
        print(f"Error cargando el historial: {e}")
        return []
