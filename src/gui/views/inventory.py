import customtkinter as ctk
from tkinter import ttk, messagebox
from src.core.product import Product
from src.utils.conversor_Moneda import format_percentege, format_to_cop

class InventoryView(ctk.CTkFrame):
    def __init__(self, master, inventory):
        super().__init__(master, fg_color="transparent")
        self.inventory = inventory
        
        # Configuración de grid para que la tabla se expanda
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        # --- 1. BARRA SUPERIOR (Búsqueda y Botón Nuevo) ---
        self.header = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20), ipady=10)

        # Entrada de búsqueda
        self.search_entry = ctk.CTkEntry(
            self.header, 
            placeholder_text="Buscar por nombre, ID o SKU...",
            width=400, 
            height=40,
            border_width=1
        )
        self.search_entry.pack(side="left", padx=20, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Botón Nuevo Producto
        self.btn_nuevo = ctk.CTkButton(
            self.header, 
            text="+ Nuevo Producto", 
            fg_color="#3D5AFE",
            hover_color="#2A3EB1", 
            height=40, 
            font=("Segoe UI", 13, "bold"),
            command=lambda: self.open_edit_window()
        )
        self.btn_nuevo.pack(side="right", padx=20)

        # --- 2. CONTENEDOR DE LA TABLA ---
        self.table_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.table_container.grid(row=1, column=0, sticky="nsew")

        # Configuración del estilo de la tabla (Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="white", 
                        foreground="black", 
                        rowheight=35, 
                        fieldbackground="white",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", 
                        background="#F2F4F7", 
                        font=("Segoe UI", 11, "bold"), 
                        borderwidth=0)
        style.map("Treeview", background=[('selected', '#3D5AFE')])

        # Definir columnas
        columns = ("id", "sku", "name", "price", "iva", "stock")
        self.tree = ttk.Treeview(self.table_container, columns=columns, show="headings")

        # Encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="PRODUCTO")
        self.tree.heading("price", text="PRECIO")
        self.tree.heading("iva", text="IVA")
        self.tree.heading("stock", text="STOCK")

        # Ajuste de columnas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("sku", width=120, anchor="center")
        self.tree.column("name", width=300, anchor="w")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("iva", width=80, anchor="center")
        self.tree.column("stock", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Binding para doble click
        self.tree.bind("<Double-1>", self.on_double_click)

        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    # --- LÓGICA DE INTERFAZ ---

    def on_search(self, event=None):
        """Filtra los productos en tiempo real."""
        criterio = self.search_entry.get().strip()
        resultados = self.inventory.search_products(criterio)
        self.update_table(resultados)

    def update_table(self, data=None):
        """Limpia y rellena la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Si no hay data (búsqueda vacía), usamos todo el inventario
        source = data if data is not None else self.inventory._products.values()
        
        for p in source:
            self.tree.insert("", "end", values=(
                p.id, 
                p.sku, 
                p.name, 
                format_to_cop(p.price), 
                format_percentege(p.iva), 
                p.stock
            ))

    def on_double_click(self, event):
        """Detecta la fila seleccionada y abre la edición."""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        # Obtener el ID del producto (columna 0)
        p_id = self.tree.item(selected_item[0])['values'][0]
        producto = self.inventory._products.get(int(p_id))
        
        if producto:
            self.open_edit_window(producto)

    def open_edit_window(self, product=None):
        """Ventana flotante para agregar o editar."""
        # Configuración de la ventana modal
        modal = ctk.CTkToplevel(self)
        modal.title("Detalle de Producto")
        modal.geometry("400x600")
        modal.after(100, lambda: modal.focus_set()) # Asegura que aparezca al frente
        modal.grab_set() # Bloquea la ventana principal

        # Título
        txt_titulo = "Editar Producto" if product else "Agregar Nuevo Producto"
        ctk.CTkLabel(modal, text=txt_titulo, font=("Segoe UI", 18, "bold")).pack(pady=20)

        # Función para crear labels y entries rápidamente
        def create_input(label_text, default_value=""):
            frame = ctk.CTkFrame(modal, fg_color="transparent")
            frame.pack(fill="x", padx=40, pady=5)
            ctk.CTkLabel(frame, text=label_text, font=("Segoe UI", 12)).pack(anchor="w")
            entry = ctk.CTkEntry(frame, width=320)
            entry.insert(0, str(default_value))
            entry.pack(pady=5)
            return entry

        # Campos
        e_name = create_input("Nombre del Producto", product.name if product else "")
        e_price = create_input("Precio Base", product.price if product else "")
        e_iva = create_input("IVA (ej: 0.19)", product.iva if product else "0.19")
        e_stock = create_input("Stock Actual", product.stock if product else "")
        e_sku = create_input("Código SKU", product.sku if product else "")

        def guardar():
            try:
                # Validaciones básicas
                name = e_name.get().strip()
                price = float(e_price.get())
                iva = float(e_iva.get())
                stock = int(e_stock.get())
                sku = e_sku.get().strip()

                if not name or not sku:
                    messagebox.showwarning("Atención", "Nombre y SKU son obligatorios.")
                    return

                if product:
                    # Actualizar objeto existente
                    product.name, product.price = name, price
                    product.iva, product.stock, product.sku = iva, stock, sku
                else:
                    # Crear nuevo
                    new_id = self.inventory._generate_next_id()
                    nuevo = Product(new_id, name, price, stock, iva, sku)
                    self.inventory.add_product(nuevo)

                self.inventory.save_to_file()
                self.update_table()
                modal.destroy()
                messagebox.showinfo("Éxito", "Datos guardados correctamente.")

            except ValueError:
                messagebox.showerror("Error", "Precio, IVA y Stock deben ser números.")

        # Botones de acción
        ctk.CTkButton(
            modal, text="Guardar Cambios", fg_color="#28a745", hover_color="#218838",
            font=("Segoe UI", 13, "bold"), command=guardar
        ).pack(pady=(30, 10), padx=40, fill="x")

        if product:
            def eliminar():
                if messagebox.askyesno("Confirmar", f"¿Eliminar '{product.name}' definitivamente?"):
                    if self.inventory.delete_product(product.id):
                        self.update_table()
                        modal.destroy()

            ctk.CTkButton(
                modal, text="Eliminar Producto", fg_color="#dc3545", hover_color="#c82333",
                command=eliminar
            ).pack(pady=10, padx=40, fill="x")

    def refresh(self):
        """Llamado por la app principal al cambiar de pestaña."""
        self.update_table()