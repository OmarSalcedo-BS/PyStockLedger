import customtkinter as ctk
from tkinter import ttk, messagebox
from src.core.product import Product
from src.utils.conversor_Moneda import format_percentege, format_to_cop


class InventoryView(ctk.CTkFrame):
    def __init__(self, master, inventory):
        super().__init__(master, fg_color="transparent")
        self.inventory = inventory

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        # --- 1. BARRA SUPERIOR ---
        self.header = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20), ipady=10)

        self.search_entry = ctk.CTkEntry(
            self.header,
            placeholder_text="Buscar por nombre, ID o SKU...",
            width=400,
            height=40,
            border_width=1,
        )
        self.search_entry.pack(side="left", padx=20, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.btn_nuevo = ctk.CTkButton(
            self.header,
            text="+ Nuevo Producto",
            fg_color="#3D5AFE",
            hover_color="#2A3EB1",
            height=40,
            font=("Segoe UI", 13, "bold"),
            command=lambda: self.open_edit_window(),
        )
        self.btn_nuevo.pack(side="right", padx=20)

        # --- 2. CONTENEDOR DE LA TABLA ---
        self.table_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.table_container.grid(row=1, column=0, sticky="nsew")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background="white", rowheight=35, font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading", background="#F2F4F7", font=("Segoe UI", 11, "bold")
        )

        # COLUMNAS ACTUALIZADAS: Añadimos COSTO
        columns = ("id", "sku", "name", "cost", "price", "iva", "stock")
        self.tree = ttk.Treeview(self.table_container, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="PRODUCTO")
        self.tree.heading("cost", text="COSTO (C)")
        self.tree.heading("price", text="PRECIO (V)")
        self.tree.heading("iva", text="IVA VENTA")
        self.tree.heading("stock", text="STOCK")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("sku", width=100, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("cost", width=100, anchor="center")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("iva", width=80, anchor="center")
        self.tree.column("stock", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

    def update_table(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        source = data if data is not None else self.inventory._products.values()

        for p in source:
            self.tree.insert(
                "",
                "end",
                values=(
                    p.id,
                    p.sku,
                    p.name,
                    format_to_cop(float(p.cost)),  # Mostramos costo
                    format_to_cop(p.price),  # Mostramos precio venta
                    format_percentege(p.tax_sale),  # Usamos tax_sale
                    p.stock,
                ),
            )

    def open_edit_window(self, product=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Gestión de Producto")
        modal.geometry("550x700")  # Aumentamos el tamaño
        modal.grab_set()

        # Título arriba (fijo)
        txt_titulo = "Editar Producto" if product else "Agregar Nuevo Producto"
        ctk.CTkLabel(modal, text=txt_titulo, font=("Segoe UI", 20, "bold")).pack(
            pady=15
        )

        # CONTENEDOR CON SCROLL (Para los inputs)
        scroll_container = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=20, pady=10)

        def create_input(master, label_text, default_value=""):
            frame = ctk.CTkFrame(master, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(frame, text=label_text, font=("Segoe UI", 12, "bold")).pack(
                anchor="w"
            )
            entry = ctk.CTkEntry(frame, height=35)
            entry.insert(0, str(default_value))
            entry.pack(fill="x", pady=5)
            return entry

        # Campos dentro del Scroll
        e_name = create_input(
            scroll_container, "Nombre del Producto", product.name if product else ""
        )
        e_sku = create_input(
            scroll_container, "Código SKU", product.sku if product else ""
        )
        e_stock = create_input(
            scroll_container, "Stock Inicial/Actual", product.stock if product else "0"
        )

        ctk.CTkLabel(
            scroll_container,
            text="--- Valores Financieros ---",
            font=("Segoe UI", 11, "italic"),
        ).pack(pady=10)

        e_cost = create_input(
            scroll_container,
            "Costo de Compra (Unitario)",
            product.cost if product else "0",
        )
        e_price = create_input(
            scroll_container,
            "Precio de Venta (Unitario)",
            product.price if product else "0",
        )
        e_tax_purchase = create_input(
            scroll_container,
            "IVA de Compra (0.19)",
            product.tax_purchase if product else "0.19",
        )
        e_tax_sale = create_input(
            scroll_container,
            "IVA de Venta (0.19)",
            product.tax_sale if product else "0.19",
        )

        def guardar():
            try:
                # Mapeo de valores
                datos = {
                    "name": e_name.get().strip(),
                    "sku": e_sku.get().strip(),
                    "price": float(e_price.get()),
                    "stock": int(e_stock.get()),
                    "cost": float(e_cost.get()),
                    "tax_purchase": float(e_tax_purchase.get()),
                    "tax_sale": float(e_tax_sale.get()),
                }

                if not datos["name"] or not datos["sku"]:
                    messagebox.showwarning("Atención", "Nombre y SKU son obligatorios.")
                    return

                if product:
                    # Actualizar objeto
                    product.name, product.sku = datos["name"], datos["sku"]
                    product.price, product.stock = datos["price"], datos["stock"]
                    product.cost = datos["cost"]
                    product.tax_purchase = datos["tax_purchase"]
                    product.tax_sale = datos["tax_sale"]
                else:
                    # Crear nuevo
                    new_id = self.inventory._generate_next_id()
                    nuevo = Product(
                        new_id,
                        datos["name"],
                        datos["sku"],
                        datos["price"],
                        datos["stock"],
                        datos["cost"],
                        datos["tax_purchase"],
                        datos["tax_sale"],
                    )
                    self.inventory.add_product(nuevo)

                self.inventory.save_to_file()
                self.update_table()
                modal.destroy()
                messagebox.showinfo("Éxito", "Producto guardado correctamente.")

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Asegúrese de ingresar números válidos en Costo, Precio, IVA y Stock.",
                )

        # Botones de acción al final (fijos fuera del scroll para que siempre se vean)
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="GUARDAR DATOS",
            fg_color="#28a745",
            hover_color="#218838",
            height=45,
            font=("Segoe UI", 13, "bold"),
            command=guardar,
        ).pack(fill="x", pady=5)

        if product:
            ctk.CTkButton(
                btn_frame,
                text="ELIMINAR PRODUCTO",
                fg_color="#dc3545",
                hover_color="#c82333",
                command=lambda: self._eliminar_producto(product, modal),
            ).pack(fill="x", pady=5)

    def _eliminar_producto(self, product, modal):
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{product.name}'?"):
            if self.inventory.delete_product(product.id):
                self.update_table()
                modal.destroy()

    def on_search(self, event=None):
        criterio = self.search_entry.get().strip()
        resultados = self.inventory.search_products(criterio)
        self.update_table(resultados)

    def on_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            p_id = self.tree.item(selected_item[0])["values"][0]
            producto = self.inventory._products.get(int(p_id))
            if producto:
                self.open_edit_window(producto)

    def refresh(self):
        self.update_table()
