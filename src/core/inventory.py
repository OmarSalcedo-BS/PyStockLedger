from src.core.product import product


class inventory:
    """
    Gestiona la colección de productos, ingresos y reportes.
    """

def __init__(self) -> None:
        # Usamos un diccionario para que buscar un producto por ID sea ultra rápido.
        # { id_del_producto: objeto_producto }
        self._products: dict[int, product] = {}

def add_product(self, product: product) -> None:
        """Añade un nuevo producto al sistema."""
        if product.id in self._products:
            raise ValueError(f"El producto con ID {product.id} ya existe.")
        self._products[product.id] = product

def get_inventory_value(self) -> float:
        """
        Calcula el valor total del inventario.
        Aquí usamos una 'comprensión de lista' (List Comprehension).
        """
        # Explicación: Creamos una lista de (precio * stock) y luego la sumamos.
        return sum([p.price * p.stock for p in self._products.values()])

def list_low_stock(self, threshold: int = 5) -> list[str]:
        """
        Retorna una lista con los nombres de productos con stock bajo.
        """
        # Comprensión con filtro 'if':
        # "Dame el nombre de cada producto SI su stock es menor al límite"
        return [p.name for p in self._products.values() if p.stock < threshold]
