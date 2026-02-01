from datetime import datetime


class Transaction:
    """
    Registra un movimiento de inventario (Entrada o Salida).
    """

    def __init__(self, product_id: int, type: str, quantity: int, reason: str = ""):
        self.product_id = product_id
        self.type = type  # "IN" o "OUT"
        self.quantity = quantity
        self.reason = reason
        # Generamos la fecha automáticamente al momento de la transacción
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        """Necesario para nuestra futura persistencia de historial."""
        return {
            "product_id": self.product_id,
            "type": self.type,
            "quantity": self.quantity,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }
