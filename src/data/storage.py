from src.data.data_handler import DataHandler
import json
import os
from src.core.transaction import Transaction
from src.core.product import Product


# Definición de la ruta donde se guardaran los datos
DATA_PATH = "data/inventory.json"
TRANS_PATH = "data/transactions.json"
PURCHASES_PATH = "data/purchases.json"
PROVIDERS_FILE = "data/providers.json"
CUSTOMERS_FILE = "data/customers.json"


def load_data(file_path="data/inventory.json"):
    """
    Ahora usa el DataHandler para asegurar que el diccionario
    que recibe el Inventory sea perfecto.
    """
    # En lugar de solo abrir el JSON, lo pasamos por el filtro de Pandas
    return DataHandler.load_and_standardize(file_path)


def save_data(products: dict, transactions: list) -> None:
    """Guarda productos y transacciones en sus respectivos archivos JSON."""
    try:
        # 1. Guardar Productos
        products_dict = {}
        for pid, p in products.items():
            if hasattr(p, "to_dict"):
                products_dict[str(pid)] = p.to_dict()
            elif isinstance(p, dict):
                products_dict[str(pid)] = p
            else:
                # Fallback for weird objects
                pass
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(products_dict, f, indent=4, ensure_ascii=False)

        # 2. Guardar Transacciones
        # Convertimos objetos Transaction a dicts usando __dict__ o manualmente
        trans_list = [t.__dict__ if hasattr(t, "__dict__") else t for t in transactions]
        with open(TRANS_PATH, "w", encoding="utf-8") as f:
            json.dump(trans_list, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Error al guardar los datos: {e}")


def load_transactions() -> list:
    """Carga el historial desde el archivo JSON."""
    if not os.path.exists(TRANS_PATH):
        return []
    try:
        with open(TRANS_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            # Forzaremos que el producto_id sea int
            history = []
            for t in raw_data:
                t["product_id"] = int(t["product_id"])
                history.append(Transaction(**t))
            return history
    except Exception as e:
        print(f"Error cargando el historial: {e}")
        return []


def save_products(self, products):
    """Guarda el diccionario de objetos Product."""
    data = {str(p_id): p.to_dict() for p_id, p in products.items()}
    with open("data/inventory.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_products(self):
    if not os.path.exists("data/inventory.json"):
        return {}
    with open("data/inventory.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            products = {}
            for p_id, d in data.items():
                # --- SOLUCIÓN AL ERROR ---
                # Buscamos 'iva' (formato viejo) o 'tax_sale' (formato nuevo)
                # Si no existe ninguno, ponemos 0.19 por defecto
                iva_valor = d.get("iva", d.get("tax_sale", 0.19))

                products[int(p_id)] = Product(
                    id=d["id"],
                    name=d["name"],
                    sku=d["sku"],
                    price=d["price"],
                    stock=d["stock"],
                    cost=d.get("cost", 0.0),  # Si no existe, inicia en 0
                    tax_purchase=d.get(
                        "tax_purchase", iva_valor
                    ),  # Usa el iva viejo como base
                    tax_sale=iva_valor,
                )
            return products
        except Exception as e:
            print(f"Error crítico al leer JSON: {e}")
            return {}


def load_providers():
    if not os.path.exists(PROVIDERS_FILE):
        # Datos iniciales para que pruebes (como los de tu imagen)
        initial_data = {
            "900123456": {
                "name": "Distribuciones Yeca S.A.S",
                "address": "Cl 45 #12-34",
                "phone": "3001234567",
            },
            "800987654": {
                "name": "Tech Solutions",
                "address": "Av Siempre Viva 123",
                "phone": "6014567890",
            },
        }
        save_providers(initial_data)
        return initial_data

    with open(PROVIDERS_FILE, "r") as f:
        return json.load(f)


def save_providers(data):
    with open(PROVIDERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_customers():
    """Carga los clientes desde el JSON o devuelve un ejemplo si no existe."""
    if not os.path.exists(CUSTOMERS_FILE):
        # Datos de ejemplo iniciales para tus sucursales
        initial_data = {
            "SUC-001": {
                "name": "Sucursal Norte",
                "address": "Calle 100 #15-20",
                "phone": "555-1234",
                "local_name": "PyStock Norte",
            }
        }
        save_customers(initial_data)
        return initial_data

    with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_customers(data):
    """Guarda el diccionario de clientes en el disco."""
    os.makedirs("data", exist_ok=True)
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
