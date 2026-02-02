import customtkinter as ctk
from tkinter import ttk
from src.utils.conversor_Moneda import format_to_cop


class InventoryView(ctk.CTkFrame):
    def __init__(self, parent, inventory_engine):
        super().__init__(parent, fg_color="transparent")
        self.inventory = inventory_engine
        self.grid_columnconfigure(0, weight=3)  # Tabla
        self.grid_columnconfigure(1, weight=1)  # Panel de Edición
        self.grid_rowconfigure(0, weight=1)

        # --- SECCIÓN TABLA ---
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Aquí va el Treeview que ya afinamos antes...
        self.setup_table()

        # --- SECCIÓN EDICIÓN (Toda la info editable) ---
        self.edit_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.edit_panel.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            self.edit_panel, text="Detalles del Producto", font=("Segoe UI", 18, "bold")
        ).pack(pady=20)

        # Campos de texto para cada propiedad
        self.entries = {}
        fields = [
            ("Nombre", "name"),
            ("Precio", "price"),
            ("Stock", "stock"),
            ("SKU", "sku"),
        ]

        for label, key in fields:
            ctk.CTkLabel(self.edit_panel, text=label).pack(padx=20, anchor="w")
            entry = ctk.CTkEntry(self.edit_panel, placeholder_text=label)
            entry.pack(fill="x", padx=20, pady=(0, 10))
            self.entries[key] = entry

        self.btn_save = ctk.CTkButton(
            self.edit_panel, text="Guardar Cambios", fg_color="#3D5AFE"
        )
        self.btn_save.pack(pady=20, padx=20, fill="x")

    def setup_table(self):
        # Insertar aquí la configuración del Treeview (columnas, headings, tags)
        pass

    def refresh(self):
        # Función para recargar los datos cuando se muestra la vista
        pass
