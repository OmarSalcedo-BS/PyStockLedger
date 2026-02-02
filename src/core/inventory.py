from src.core.product import Product
from src.data.storage import load_data, save_data, load_transactions
from src.core.transaction import Transaction

class Inventory:
    """
    Gestiona la colección de productos, ingresos y reportes.
    """

    def __init__(self) -> None:
        self._products = {}
        self._history = []
        self.load_from_storage()

    def load_from_storage(self) -> None:
        """Carga y convierte los datos crudos en objetos Product."""
        raw_data = load_data() 
        self._history = load_transactions()
        self._products = {}

        for p_id, p_data in raw_data.items():
            # Manejo del error que encontraste: 
            # Si p_data es una lista o dict anidado con "0", tomamos el primer elemento
            if isinstance(p_data, list) and len(p_data) > 0:
                p_data = p_data[0]
            elif isinstance(p_data, dict) and "0" in p_data:
                p_data = p_data["0"]

            try:
                nuevo_producto = Product(
                    id=int(p_id),
                    name=p_data.get('name', 'Sin Nombre'),
                    price=float(p_data.get('price', 0.0)),
                    stock=int(p_data.get('stock', 0)),
                    iva=float(p_data.get('iva', 0.0)),
                    sku=p_data.get('sku', 'N/A')
                )
                self._products[int(p_id)] = nuevo_producto
            except (KeyError, TypeError, ValueError) as e:
                print(f"Error cargando producto {p_id}: {e}")

    def _generate_next_id(self) -> int:
        if not self._products:
            return 1
        return max(self._products.keys()) + 1

    def add_product(self, product: Product) -> None:
        if product.id in self._products:
            raise ValueError(f"El producto con ID {product.id} ya existe.")
        self._products[product.id] = product
        self.save_to_file()

    def save_to_file(self) -> None:
        """
        Convierte los objetos Product de vuelta a diccionarios simples 
        para que save_data no cree llaves extra.
        """
        # Convertimos los objetos a un formato de diccionario plano
        dict_para_guardar = {
            str(p.id): {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "stock": p.stock,
                "iva": p.iva,
                "sku": p.sku
            }
            for p in self._products.values()
        }
        save_data(dict_para_guardar, self._history)

    def register_movement(self, product_id: int, quantity: int, type: str, reason: str = "") -> None:
        if product_id not in self._products:
            raise ValueError(f"ID {product_id} no encontrado.")

        product = self._products[product_id]
        amount = quantity if type == "IN" else -quantity

        try:
            product.update_stock(amount)
            new_transaction = Transaction(product_id, type, quantity, reason)
            self._history.append(new_transaction)
            self.save_to_file()
        except ValueError as e:
            raise ValueError(f"Error en movimiento: {e}")

    def get_inventory_value(self) -> float:
        return sum([p.price * p.stock for p in self._products.values()])

    def search_products(self, criterio: str) -> list[Product]:
        criterio = criterio.lower()
        return [
            p for p in self._products.values()
            if criterio in p.name.lower() or criterio in str(p.id) or criterio in p.sku.lower()
        ]

    def get_financial_summary(self) -> dict:
        summary = {"in_total": 0.0, "out_total": 0.0, "current_value": self.get_inventory_value()}
        for t in self._history:
            product = self._products.get(t.product_id)
            if product:
                value = t.quantity * product.price
                if t.type == "IN":
                    summary["in_total"] += value
                else:
                    summary["out_total"] += value
        return summary

    def reload(self):
        """Vuelve a cargar los datos correctamente."""
        self.load_from_storage()