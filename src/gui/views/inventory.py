import customtkinter as ctk
from tkinter import ttk, messagebox
from src.utils.conversor_Moneda import format_to_cop, format_percentege

class InventoryView(ctk.CTkFrame):
    def __init__(self, parent, inventory):
        super().__init__(parent, fg_color="transparent")
        self.inventory = inventory
        self.selected_id = None 

        self.grid_columnconfigure(0, weight=3) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # --- CONTENEDOR TABLA ---
        self.container_table = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.container_table.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        self.tree_wrapper = ctk.CTkFrame(self.container_table, fg_color="transparent")
        self.tree_wrapper.pack(fill="both", expand=True, padx=20, pady=20)
        self.setup_treeview()

        # --- PANEL EDICIÓN (Con Scroll Vertical) ---
        self.panel_edit = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.panel_edit.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.panel_edit, text="Editar Producto", 
                     font=("Segoe UI", 20, "bold"), text_color="#1A1C1E").pack(pady=(30, 10))

        # El scroll vertical para los campos de texto
        self.scroll_editor = ctk.CTkScrollableFrame(self.panel_edit, fg_color="transparent", height=450)
        self.scroll_editor.pack(fill="both", expand=True, padx=10)

        self.entries = {}
        campos = [
            ("Nombre del Producto", "name"),
            ("Precio Base", "price"),
            ("IVA (Ej: 0.19)", "iva"),
            ("Stock Actual", "stock"),
            ("Código SKU", "sku")
        ]
        
        for label, key in campos:
            ctk.CTkLabel(self.scroll_editor, text=label, font=("Segoe UI", 12, "bold"), 
                         text_color="#555555").pack(padx=15, anchor="w", pady=(10, 0))
            e = ctk.CTkEntry(self.scroll_editor, height=40, corner_radius=8,
                             fg_color="#F9F9F9", border_color="#E0E0E0", text_color="black")
            e.pack(fill="x", padx=15, pady=(0, 5))
            self.entries[key] = e

        self.btn_save = ctk.CTkButton(self.panel_edit, text="Actualizar Datos", 
                                      fg_color="#3D5AFE", height=45, corner_radius=10, 
                                      font=("Segoe UI", 14, "bold"),
                                      command=self.save_changes)
        self.btn_save.pack(pady=20, padx=25, fill="x")

    def setup_treeview(self):
        sy = ttk.Scrollbar(self.tree_wrapper, orient="vertical")
        sx = ttk.Scrollbar(self.tree_wrapper, orient="horizontal")
        
        self.tree = ttk.Treeview(self.tree_wrapper, columns=("id", "sku", "name", "price", "stock", "iva"), 
                                 show="headings", yscrollcommand=sy.set, xscrollcommand=sx.set)
        
        sy.config(command=self.tree.yview)
        sx.config(command=self.tree.xview)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # El scroll horizontal se activa por el ancho (300) de PRODUCTO
        cols = {"id": ("ID", 50), "sku": ("SKU", 120), "name": ("PRODUCTO", 300), 
                "price": ("PRECIO", 120), "stock": ("STOCK", 80), "iva": ("IVA", 80)}
        for id, (txt, w) in cols.items():
            self.tree.heading(id, text=txt)
            self.tree.column(id, width=w, minwidth=w, anchor="center" if id != "name" else "w")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection: 
            return
        self.selected_id = int(self.tree.item(selection[0])["values"][0])
        p = self.inventory._products.get(self.selected_id)
        if p:
            for key in ["name", "price", "iva", "stock", "sku", "iva"]:
                self.entries[key].delete(0, 'end')
                # getattr busca el atributo en el objeto Product
                self.entries[key].insert(0, str(getattr(p, key, "N/A")))

    def save_changes(self):
        if not self.selected_id: 
            return
        try:
            p = self.inventory._products[self.selected_id]
            p.name = self.entries["name"].get()
            p.price = float(self.entries["price"].get())
            p.iva = float(self.entries["iva"].get())
            p.stock = int(self.entries["stock"].get())
            p.sku = self.entries["sku"].get()

            self.inventory.save_to_file()
            messagebox.showinfo("Éxito", "Producto actualizado en disco.")
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Verifica los números ingresados.")

    def refresh(self):
        for item in self.tree.get_children(): 
            self.tree.delete(item)
        for p in self.inventory._products.values():
            self.tree.insert("", "end", values=(
                p.id, getattr(p, 'sku', 'N/A'), p.name, format_to_cop(p.price), p.stock, format_percentege(p.iva)
            ))