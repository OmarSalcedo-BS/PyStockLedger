from datetime import datetime


class Transaction:
    """
    Registra un movimiento de inventario (Entrada o Salida).
    """

    def __init__(
        self,
        product_id: int,
        type: str,
        quantity: int,
        reason: str = "",
        cost: float = 0.0,
        tax: float = 0.0,
        discount: float = 0.0,
        timestamp: str = None,
    ):
        self.product_id = product_id
        self.type = type
        self.quantity = quantity
        self.reason = reason
        self.cost = cost
        self.tax = tax
        self.discount = discount
        # Si nos pasan timestamp (al cargar desde disco), lo usamos. Si no, generamos uno nuevo.
        self.timestamp = (
            timestamp if timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def to_dict(self) -> dict:
        """Necesario para nuestra futura persistencia de historial."""
        return {
            "product_id": self.product_id,
            "type": self.type,
            "quantity": self.quantity,
            "reason": self.reason,
            "cost": self.cost,
            "tax": self.tax,
            "discount": getattr(self, "discount", 0.0),  # Fallback por si acaso
            "timestamp": self.timestamp,
        }
