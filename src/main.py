from core.product import Product
from core.inventory import Inventory
from utils.conversor_Moneda import format_to_cop

def run():
    #Inicializamos el "cerebro" de la aplicacion
    mi_bodega = Inventory()
    
    print("--- PyStockLedger: Iniciando el programa ---")

    try:
        #1. Creamos productos (Instanciando los objetos)
        p1 = Product(id=1, name ="Aceite de motor", price=15000.00, stock=10, iva=0.19)
        p2 = Product(id=2, name="Filtro de aire", price=25000.00, stock=5, iva=0.19)
        p3 = Product(id=3, name="Freno de mano", price=120000.00, stock=2, iva=0.19)
        
        #2. Agregamos los productos a la bodega
        mi_bodega.add_product(p1)
        mi_bodega.add_product(p2)
        mi_bodega.add_product(p3)
       
        #3. Mostramos los productos
        print(f" Se han cargado {len(mi_bodega._products)} productos")
        for product in mi_bodega._products.values():
            print(product)

        #4. Obtenemos el valor total de la bodega
        total = mi_bodega.get_inventory_value()
        print(f"El valor total de la bodega es: {format_to_cop(total)}")

        #5. Probamos el reporte de stock bajo
        # Queremos ver productos con menos de 5 unidades
        alerta_stock = mi_bodega.list_low_stock(threshold=5)
        print(f"Alerta de Stock Bajo (menos de 5): {alerta_stock}")

    except ValueError as e:
        print(f"Error de validación: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    run()


        
        