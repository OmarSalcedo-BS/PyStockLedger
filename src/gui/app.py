import customtkinter as ctk
from src.core.inventory import Inventory
from src.utils.conversor_Moneda import format_to_cop

# Configuración global de la apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PyStockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Configuración de Ventana Principal
        self.title("PyStock Ledger - Panel de Control")
        self.geometry("1100x700")
        
        # 2. Inicializar Motor Lógico
        self.inventory = Inventory()

        # 3. Configuración del Layout (Grid System)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA LATERAL (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Empuja lo de abajo

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="📦 PyStock", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_refresh = ctk.CTkButton(
            self.sidebar_frame, 
            text="Actualizar Tabla", 
            command=self.refresh_data
        )
        self.btn_refresh.grid(row=1, column=0, padx=20, pady=10)

        # --- ÁREA CENTRAL ---
        self.main_container = ctk.CTkFrame(self, corner_radius=15)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1) # La tabla se expande

        # A. DASHBOARD (Métricas rápidas)
        self.dash_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.dash_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.dash_frame.grid_columnconfigure((0, 1), weight=1)

        # Card: Valor Total
        self.card_val = ctk.CTkFrame(self.dash_frame, fg_color="#2b2b2b", corner_radius=10)
        self.card_val.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.lbl_val_data = ctk.CTkLabel(
            self.card_val, 
            text="Valor: $ 0", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#1f6aa5"
        )
        self.lbl_val_data.pack(pady=15)

        # Card: Alertas de Stock
        self.card_low = ctk.CTkFrame(self.dash_frame, fg_color="#2b2b2b", corner_radius=10)
        self.card_low.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.lbl_low_data = ctk.CTkLabel(
            self.card_low, 
            text="Alertas: 0", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#e63946"
        )
        self.lbl_low_data.pack(pady=15)

        # B. BARRA DE BÚSQUEDA
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.update_search) 
        
        self.search_entry = ctk.CTkEntry(
            self.main_container, 
            placeholder_text="Buscar producto por nombre o SKU...", 
            textvariable=self.search_var, 
            width=500,
            height=35
        )
        self.search_entry.grid(row=1, column=0, padx=20, pady=15)

        # C. TABLA DE RESULTADOS
        self.scrollable_table = ctk.CTkScrollableFrame(
            self.main_container, 
            label_text="ID   |   PRODUCTO   |   PRECIO   |   STOCK   |   SKU",
            label_font=ctk.CTkFont(weight="bold")
        )
        self.scrollable_table.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        self.scrollable_table.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Carga inicial de datos
        self.render_inventory()

    # --- MÉTODOS DE ACCIÓN ---

    def update_search(self, *args):
        """Filtra la tabla en tiempo real mientras el usuario escribe."""
        criterio = self.search_var.get()
        if criterio.strip() == "":
            self.render_inventory()
        else:
            resultados = self.inventory.search_products(criterio)
            self.render_inventory(lista_productos=resultados)

    def refresh_data(self):
        """Sincroniza el inventario con el archivo JSON y refresca la UI."""
        try:
            self.inventory.reload() 
            self.render_inventory()
            print("Inventario actualizado desde el almacenamiento.")
        except Exception as e:
            print(f"Error al refrescar: {e}")

    def render_inventory(self, lista_productos=None):
        """Limpia la tabla y dibuja los elementos del inventario."""
        # Limpieza de widgets existentes
        for child in self.scrollable_table.winfo_children():
            child.destroy()

        # Selección de fuente de datos
        datos = lista_productos if lista_productos is not None else self.inventory._products.values()

        # Dibujado de filas
        for i, p in enumerate(datos):
            ctk.CTkLabel(self.scrollable_table, text=str(p.id)).grid(row=i, column=0, pady=5)
            ctk.CTkLabel(self.scrollable_table, text=p.name, anchor="w").grid(row=i, column=1, sticky="w", padx=10)
            ctk.CTkLabel(self.scrollable_table, text=format_to_cop(p.price)).grid(row=i, column=2)
            
            # Resaltado de stock bajo
            stock_color = "#e63946" if p.stock < 5 else "white"
            ctk.CTkLabel(self.scrollable_table, text=str(p.stock), text_color=stock_color, font=ctk.CTkFont(weight="bold" if p.stock < 5 else "normal")).grid(row=i, column=3)
            
            ctk.CTkLabel(self.scrollable_table, text=p.sku).grid(row=i, column=4)

        # Actualización de Métricas en el Dashboard
        self.update_dashboard()

    def update_dashboard(self):
        """Calcula y muestra los totales financieros y alertas."""
        summary = self.inventory.get_financial_summary()
        low_stock_count = len([p for p in self.inventory._products.values() if p.stock < 5])
        
        self.lbl_val_data.configure(text=f"Valor Total: {format_to_cop(summary['current_value'])}")
        self.lbl_low_data.configure(text=f"Alertas de Stock: {low_stock_count}")

if __name__ == "__main__":
    app = PyStockApp()
    app.mainloop()