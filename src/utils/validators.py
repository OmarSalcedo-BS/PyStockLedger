
def get_validated_input(prompt: str, expected_type: type, min_value=None):
    """
    Pide un dato al usuario hasta que sea válido.
    """
    while True:
        try:
            value = expected_type(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Error: El valor mínimo es {min_value}.")
                continue
            return value
        except ValueError:
            print(f"Error: Entrada inválida. Se esperaba un {expected_type.__name__}.")