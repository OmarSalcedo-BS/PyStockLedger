import os
from src.core.product import Product
from src.core.inventory import Inventory
from src.utils.validators import get_validated_input


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def seed_data(inventory: Inventory):
    """Carga 10 productos iniciales para pruebas."""
    productos_base = [
        {"name": "Laptop Dell XPS", "price": 4500000, "stock": 5, "sku": "DELL-001"},
        {"name": "Mouse Logi MX", "price": 350000, "stock": 12, "sku": "LOGI-202"},
        {"name": "Teclado Keychron", "price": 580000, "stock": 8, "sku": "KEY-K2"},
        {"name": "Monitor 4K ASUS", "price": 1800000, "stock": 4, "sku": "ASUS-4K"},
        {"name": "Disco SSD 1TB", "price": 420000, "stock": 20, "sku": "SAMS-SSD"},
        {"name": "Memoria RAM 16GB", "price": 280000, "stock": 15, "sku": "KING-RAM"},
        {"name": "Cámara Web HD", "price": 150000, "stock": 2, "sku": "LOGI-C920"},
        {"name": "Silla Ergonómica", "price": 850000, "stock": 6, "sku": "CHAIR-PRO"},
        {"name": "Escritorio Elevable", "price": 1200000, "stock": 3, "sku": "DESK-UP"},
        {"name": "Audífonos Sony XM5", "price": 1600000, "stock": 7, "sku": "SONY-XM5"},
    ]

    for p in productos_base:
        nuevo_id = inventory._generate_next_id()
        nuevo_p = Product(id=nuevo_id, **p)
        try:
            inventory.add_product(nuevo_p)
        except ValueError:
            continue  # Si ya existe por nombre o ID, lo salta

    print("productos cargados exitosamente.")


def menu():
    clear_screen()
    inventory = Inventory()

    while True:
        print("\n" + "=" * 40)
        print("   📦 PYSTOCK LEDGER - SISTEMA DE CONTROL")
        print("=" * 40)
        print("1. Agregar Producto (Manual)")
        print("2. Registrar Movimiento (IN/OUT)")
        print("3. Ver Inventario Completo")
        print("4. Cargar 10 Productos de Prueba (Seed)")
        print("5. Ver Historial de Movimientos")
        print("6. Buscar Productos")
        print("7. Ver Resumen Financiero")
        print("8. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            print(
                f"\n--- Nuevo Producto (ID Sugerido: {inventory._generate_next_id()}) ---"
            )
            sku = input("SKU/Código (Enter para omitir): ") or "N/A"
            nombre = input("Nombre: ").strip()
            precio = get_validated_input("Precio: ", float, min_value=0)
            stock = get_validated_input("Stock Inicial: ", int, min_value=0)

            try:
                nuevo_p = Product(
                    inventory._generate_next_id(), nombre, precio, stock, sku=sku
                )
                inventory.add_product(nuevo_p)
                print("Producto guardado.")
            except ValueError as e:
                print(f"Error: {e}")

        elif opcion == "2":
            id_p = get_validated_input("ID del producto: ", int)
            cant = get_validated_input("Cantidad: ", int, min_value=1)
            tipo = input("Tipo (IN = Entrada / OUT = Salida): ").upper()
            motivo = input("Motivo/Referencia: ")

            try:
                inventory.register_movement(id_p, cant, tipo, motivo)
            except ValueError as e:
                print(f" Error: {e}")

        elif opcion == "3":
            print("\n" + "-" * 60)
            print(
                f"{'SKU':<10} | {'ID':<4} | {'PRODUCTO':<20} | {'PRECIO':<12} | {'STOCK':<6} | {'IVA':<6} "
            )
            print("-" * 60)
            for p in inventory._products.values():
                # F-string con alineación: < a la izquierda, > a la derecha
                print(
                    f"{p.sku:<10} | {p.id:<4} | {p.name[:20]:<20} | ${p.price:<11,.0f} | {p.stock:<6} | {p.iva:<6}"
                )

        elif opcion == "4":
            seed_data(inventory)

        elif opcion == "5":  # Nueva opción
            print("\n" + "-" * 80)
            print(
                f"{'FECHA':<20} | {'TIPO':<5} | {'CANT':<5} | {'PRODUCTO':<15} | {'MOTIVO'}"
            )
            print("-" * 80)
            for t in inventory._history:
                # Buscamos el nombre del producto para que el reporte sea legible
                p_name = (
                    inventory._products[t.product_id].name
                    if t.product_id in inventory._products
                    else "Desconocido"
                )
                print(
                    f"{t.timestamp:<20} | {t.type:<5} | {t.quantity:<5} | {p_name:<15} | {t.reason}"
                )

        elif opcion == "6":
            clear_screen()
            print("\n--- Búsqueda de Productos ---")
            criterio = input("Escriba el SKU o nombre a buscar: ").strip()
            if not criterio:
                print("Debe ingresar un criterio de búsqueda.")
                continue

            resultados = inventory.search_products(criterio)

            if not resultados:
                print(f"No se encontraron productos con el criterio '{criterio}'.")
                continue

            else:
                print(
                    f"\n--- Se encontraron {len(resultados)} con el criterio  '{criterio}' ---"
                )
                print("-" * 60)
                print(
                    f"{'SKU':<10} | {'ID':<4} | {'PRODUCTO':<20} | {'PRECIO':<12} | {'STOCK':<6} | {'IVA':<6} "
                )
                print("-" * 60)
                for p in resultados:
                    print(
                        f"{p.sku:<10} | {p.id:<4} | {p.name[:20]:<20} | ${p.price:<11,.0f} | {p.stock:<6} | {p.iva:<6}"
                    )
                input("\nPresiona Enter para continuar...")

        elif opcion == "7":
            clear_screen()
            print("\n--- Resumen Financiero ---")
            summary = inventory.get_financial_summary()
            print(f"Ingresos Totales: ${summary['in_total']:,.0f}")
            print(f"Egresos Totales: ${summary['out_total']:,.0f}")
            print(f"Valor Actual del Inventario: ${summary['current_value']:,.0f}")
            input("\nPresiona Enter para continuar...")

        elif opcion == "8":
            print("¡Gracias por usar PyStock Ledger! Saliendo...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()
