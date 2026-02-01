def format_to_cop(amount: float) -> str:
    """
    Convierte un valor numérico a formato de moneda colombiana (COP).
    
    Args:
        amount (float): El valor numérico a formatear.
        
    Returns:
        str: El valor formateado (ej: $ 1.200.500).
    """

    return f"$ {amount:,.0f}".replace(",", ".")

def format_percentege(value: float) -> str:
    """Convierte un decimal a formato de porcentaje (ej: 0.19 -> 19%)."""
    return f"{value * 100:.0f}%"