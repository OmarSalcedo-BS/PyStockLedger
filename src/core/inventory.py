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
            # Manejo de compatibilidad si p_data viene anidado
            if isinstance(p_data, list) and len(p_data) > 0:
                p_data = p_data[0]
            elif isinstance(p_data, dict) and "0" in p_data:
                p_data = p_data["0"]

            try:
                # Extraemos el IVA antiguo o los nuevos
                iva_fallback = float(p_data.get('iva', 0.19))
                
                nuevo_producto = Product(
                    id=int(p_id),
                    name=p_data.get('name', 'Sin Nombre'),
                    sku=p_data.get('sku', 'N/A'),
                    price=float(p_data.get('price', 0.0)),
                    stock=int(p_data.get('stock', 0)),
                    cost=float(p_data.get('cost', 0.0)), # Nuevo atributo
                    tax_purchase=float(p_data.get('tax_purchase', iva_fallback)), # Nuevo
                    tax_sale=float(p_data.get('tax_sale', iva_fallback))  # Nuevo
                )
                self._products[int(p_id)] = nuevo_producto
            except (KeyError, TypeError, ValueError) as e:
                print(f"Error crítico cargando producto {p_id}: {e}")

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
        Sincroniza el estado actual de los productos con el almacenamiento JSON.
        Maneja tanto objetos Product como diccionarios para evitar errores de atributo.
        """
        dict_para_guardar = {}
        
        for p_id, p in self._products.items():
            # Si 'p' es un objeto de la clase Product
            if hasattr(p, 'to_dict'):
                dict_para_guardar[str(p_id)] = p.to_dict()
            # Si 'p' es un diccionario (por si acaso quedó algo del formato viejo)
            elif isinstance(p, dict):
                dict_para_guardar[str(p_id)] = p
            else:
                print(f"Aviso: El producto {p_id} tiene un formato desconocido.")

        # Aseguramos que el historial sea una lista de diccionarios antes de guardar
        historial_serializado = []
        for t in self._history:
            if hasattr(t, 'to_dict'):
                historial_serializado.append(t.to_dict())
            else:
                historial_serializado.append(t)

        try:
            save_data(dict_para_guardar, historial_serializado)
        except Exception as e:
            print(f"Error crítico al guardar en disco: {e}")

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
        """Calcula el valor del inventario basado en el COSTE de compra (más preciso)."""
        return sum([p.cost * p.stock for p in self._products.values()])

    def search_products(self, criterio: str) -> list[Product]:
        criterio = criterio.lower()
        return [
            p for p in self._products.values()
            if criterio in p.name.lower() or criterio in str(p.id) or criterio in p.sku.lower()
        ]

    def get_financial_summary(self) -> dict:
        """Resumen financiero basado en costos y precios de venta."""
        summary = {
            "inventory_cost": self.get_inventory_value(),
            "potential_revenue": sum([p.price * p.stock for p in self._products.values()]),
            "in_count": sum(1 for t in self._history if t.type == "IN"),
            "out_count": sum(1 for t in self._history if t.type == "OUT")
        }
        return summary

    def delete_product(self, product_id: int) -> bool:
        if product_id in self._products:
            del self._products[product_id]
            self.save_to_file()
            return True
        return False

    def reload(self):
        self.load_from_storage()