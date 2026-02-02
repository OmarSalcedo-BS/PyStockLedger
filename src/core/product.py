from src.utils.conversor_Moneda import format_to_cop, format_percentege


class Product:
    def __init__(
        self,
        id,
        name,
        sku,
        price,
        stock,
        cost=0.0,
        tax_purchase=0.19,
        tax_sale=0.19,
        **kwargs,
    ):
        # 1. Manejo de compatibilidad con JSON viejo
        # Si en el JSON viene 'iva', lo usamos para los nuevos campos si estos vienen en 0
        old_iva = kwargs.get("iva", 0.19)

        self.id = id
        self.name = name
        self.sku = sku
        self.price = float(price)
        self.stock = int(stock)
        self.cost = float(cost)

        # Asignamos priorizando los nombres nuevos, pero aceptando el viejo
        self.tax_purchase = float(tax_purchase if tax_purchase != 0.19 else old_iva)
        self.tax_sale = float(tax_sale if tax_sale != 0.19 else old_iva)

        # 2. Validaciones relajadas (Evitan que el programa explote al cargar)
        if self.price < 0 or self.stock < 0 or self.cost < 0:
            raise ValueError("Valores numéricos no pueden ser negativos.")

    def __str__(self) -> str:
        # Corregido: usando los nombres nuevos de atributos
        return f"[{self.id}] {self.name} - {format_to_cop(self.price)} (Stock: {self.stock}, IVA Venta: {format_percentege(self.tax_sale)})"

    def calculate_total_price(self) -> float:
        """Calcula el precio de venta incluyendo su IVA."""
        return self.price * (1 + self.tax_sale)

    def update_stock(self, amount: int) -> None:
        if self.stock + amount < 0:
            raise ValueError(
                f"Stock insuficiente para {self.name}. Disponible: {self.stock}"
            )
        self.stock += amount

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "price": self.price,
            "stock": self.stock,
            "cost": self.cost,
            "tax_purchase": self.tax_purchase,
            "tax_sale": self.tax_sale,
        }
