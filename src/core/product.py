class Product:
    """
    Representa un producto genérico dentro del sistema de inventario.

    Attributes:
        id (int): Identificador único del producto.
        name (str): Nombre comercial.
        price (float): Precio unitario (debe ser positivo).
        stock (int): Cantidad disponible (debe ser >= 0).
        iva (float): Porcentaje de IVA en decimal (ej: 0.19).
    """

    def __init__(self, id: int, name: str, price: float, stock: int = 0, iva: float = 0.19) -> None:
        if price < 0 or stock < 0:
            raise ValueError("El precio y el stock inicial no pueden ser negativos.")
        
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.iva = iva

    def __str__(self) -> str:
        return f"[{self.id}] {self.name} - ${self.price:.2f} (Stock: {self.stock}, IVA: {self.iva*100}%)"

    def calculate_total_price(self) -> float:
        """Calcula el precio del producto incluyendo el IVA."""
        return self.price * (1 + self.iva)

    def update_stock(self, amount: int) -> None:
        """
        Actualiza el stock sumando (ingreso) o restando (egreso) una cantidad.
        
        Args:
            amount (int): Cantidad a modificar.
        Raises:
            ValueError: Si el stock resultante es menor a cero.
        """
        if self.stock + amount < 0:
            raise ValueError(f"Stock insuficiente para {self.name}. Disponible: {self.stock}")
        self.stock += amount