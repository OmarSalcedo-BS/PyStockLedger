from src.data.data_handler import DataHandler
import json
import os
from core.transaction import Transaction



# Definición de la ruta donde se guardaran los datos
DATA_PATH = "data/inventory.json"
TRANS_PATH = "data/transactions.json"


def load_data(file_path="data/inventory.json"):
    """
    Ahora usa el DataHandler para asegurar que el diccionario 
    que recibe el Inventory sea perfecto.
    """
    # En lugar de solo abrir el JSON, lo pasamos por el filtro de Pandas
    return DataHandler.load_and_standardize(file_path)

def save_data(products_dict, history_list, file_path="data/inventory.json"):
    """
    Sigue siendo necesario para escribir en el archivo.
    """
    # Aquí puedes usar Pandas para guardar como CSV o JSON
    import pandas as pd
    df = pd.DataFrame.from_dict(products_dict, orient='index')
    df.to_json(file_path, orient='index', indent=4)

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
