from src.core.product import Product
from src.data.storage import load_data, save_data, load_transactions
from src.core.transaction import Transaction


class Inventory:
    """
    Gestiona la colección de productos, ingresos y reportes.
    """

    def __init__(self) -> None:
        # cargar los datos al iniciar
        self._products = load_data()
        self._history = load_transactions()  # Se carga la lista de transacciones

    def _generate_next_id(self) -> int:
        """Busca el ID más alto y le suma 1."""
        if not self._products:
            return 1
        return max(self._products.keys()) + 1



    def add_product(self, product: Product) -> None:
        """Añade un nuevo producto al sistema."""
        if product.id in self._products:
            raise ValueError(f"El producto con ID {product.id} ya existe.")
        self._products[product.id] = product
        self.save_to_file()  # Guardamos los datos

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

    def save_to_file(self) -> None:
        """Pasa tanto productos como historial al storage."""
        save_data(self._products, self._history)

    def register_movement(
        self, product_id: int, quantity: int, type: str, reason: str = ""
    ) -> None:
        """
        Registra un movimiento, actualiza el stock del producto y guarda la transacción.
        """
        # 1. Validar existencia
        if product_id not in self._products:
            raise ValueError(f"ID {product_id} no encontrado.")

        product = self._products[product_id]

        # 2. Intentar actualizar el stock usando el método del Producto
        # Si quantity es egreso, la pasamos negativa.
        amount = quantity if type == "IN" else -quantity

        try:
            product.update_stock(amount)  # Aquí ya se lanza ValueError si no hay stock

            # 3. Si el stock se actualizó con éxito, creamos la transacción
            new_transaction = Transaction(product_id, type, quantity, reason)

            # Guardamos en un historial global que definiremos en el __init__
            self._history.append(new_transaction)

            # 4. Persistencia
            self.save_to_file()
            print(f"Movimiento registrado: {type} de {product.name}")

        except ValueError as e:
            # Re-lanzamos el error para que la UI lo muestre
            raise ValueError(f"Error en movimiento: {e}")
