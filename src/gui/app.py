import customtkinter as ctk
from tkinter import ttk, messagebox
from src.core.inventory import Inventory
from src.utils.conversor_Moneda import format_to_cop

# Configuración de apariencia
ctk.set_appearance_mode("dark")


class PyStockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PyStock Ledger Pro - High Performance")
        self.geometry("1100x700")
        
        # 1. Inicializar Motor Lógico
        self.inventory = Inventory()
        self._search_job = None

        # 2. Configuración de Estilos para Treeview (Tabla Nativa)
        self.style = ttk.Style()
        self.style.theme_use("default")
        
        self.style.configure("Treeview", 
            background="#2b2b2b", 
            foreground="white", 
            fieldbackground="#2b2b2b", 
            borderwidth=0,
            font=("Segoe UI", 10),
            rowheight=35) # Filas más altas para mejor legibilidad

        # Estilo para la selección
        self.style.map("Treeview", background=[('selected', '#1f6aa5')])
        
        # Estilo para los encabezados
        self.style.configure("Treeview.Heading", 
            background="#333333", 
            foreground="white", 
            relief="flat",
            font=("Segoe UI", 10, "bold"))

        # --- TAGS DE COLOR ---
        # Configuramos la etiqueta 'low_stock' para que pinte la fila de rojo
        self.tree_font_bold = ("Segoe UI", 10, "bold")
        # Nota: En Windows/Linux, tag_configure maneja el foreground directamente
        self.style.configure("Treeview", foreground="white") 

        # 3. Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="📦 PyStock", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, padx=20, pady=20)
        
        ctk.CTkButton(self.sidebar, text="Actualizar Datos", command=self.refresh_data).grid(row=1, column=0, padx=20, pady=10)
        
        # --- ÁREA CENTRAL ---
        self.main_container = ctk.CTkFrame(self, corner_radius=15)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)

        # Dashboard de Resumen
        self.lbl_val_data = ctk.CTkLabel(self.main_container, text="Cargando resumen...", font=("Segoe UI", 18, "bold"), text_color="#1f6aa5")
        self.lbl_val_data.grid(row=0, column=0, pady=15)

        # Buscador en Tiempo Real
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.main_container, 
            placeholder_text="🔍 Escriba para buscar en tiempo real...", 
            textvariable=self.search_var, 
            width=500,
            height=35
        )
        self.search_entry.grid(row=1, column=0, padx=20, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_key_release)

        # TABLA TREEVIEW
        columns = ("id", "nombre", "precio", "stock", "sku")
        self.tree = ttk.Treeview(self.main_container, columns=columns, show="headings")
        
        # Definir encabezados y anchos
        headers = {"id": "ID", "nombre": "PRODUCTO", "precio": "PRECIO", "stock": "STOCK", "sku": "SKU"}
        for col, text in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor="center")
        
        self.tree.column("nombre", width=350, anchor="w") # Nombre alineado a la izquierda
        self.tree.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        # Configurar el color rojo para el Tag
        self.tree.tag_configure('low_stock', foreground='#e63946')

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=2, column=1, sticky="ns")

        # --- EVENTOS ---
        self.tree.bind("<Double-1>", self.on_item_double_click)

        # Carga inicial
        self.render_inventory()

    # --- LÓGICA DE LA INTERFAZ ---

    def on_key_release(self, event):
        """Debounce de 100ms para búsqueda ultra rápida."""
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(100, self.update_search)

    def update_search(self):
        criterio = self.search_var.get().lower()
        if not criterio:
            self.render_inventory()
        else:
            resultados = self.inventory.search_products(criterio)
            self.render_inventory(lista_productos=resultados)

    def on_item_double_click(self, event):
        """Maneja el registro de salida al hacer doble click."""
        selection = self.tree.selection()
        if not selection: return

        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        
        p_id = int(values[0])
        p_name = values[1]
        
        # Pedir cantidad al usuario
        dialog = ctk.CTkInputDialog(text=f"¿Cuántas unidades de '{p_name}' salieron?", title="Registrar Salida")
        respuesta = dialog.get_input()
        
        if respuesta:
            try:
                cantidad = int(respuesta)
                if cantidad <= 0: raise ValueError()
                
                # Ejecutar en el Core
                success, msg = self.inventory.register_movement(p_id, cantidad, "OUT", "Venta desde Panel GUI")
                
                if success:
                    self.render_inventory() # Actualiza tabla y dashboard
                    messagebox.showinfo("Éxito", msg)
                else:
                    messagebox.showerror("Sin Stock", msg)
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un número entero válido.")

    def render_inventory(self, lista_productos=None):
        """Renderiza la tabla usando Tags para resaltar stock bajo."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        datos = lista_productos if lista_productos is not None else self.inventory._products.values()

        for p in datos:
            # Aplicar Tag si el stock es crítico
            tag = ('low_stock',) if p.stock < 5 else ()
            
            self.tree.insert("", "end", values=(
                p.id, 
                p.name, 
                format_to_cop(p.price), 
                p.stock, 
                p.sku
            ), tags=tag)
        
        # Actualizar métricas del dashboard
        summary = self.inventory.get_financial_summary()
        self.lbl_val_data.configure(text=f"Valor Total en Almacén: {format_to_cop(summary['current_value'])}")

    def refresh_data(self):
        """Recarga manual desde el archivo JSON."""
        self.inventory.reload()
        self.render_inventory()
        messagebox.showinfo("Sincronización", "Sincronizado con base de datos JSON.")

if __name__ == "__main__":
    app = PyStockApp()
    app.mainloop()