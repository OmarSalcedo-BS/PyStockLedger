import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import csv
from datetime import datetime

class MovementsView(ctk.CTkFrame):
    def __init__(self, master, inventory):
        super().__init__(master, fg_color="transparent")
        self.inventory = inventory
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_widgets()

        # Carga inicial de datos
        self.after(100, self.refresh)

    def _create_widgets(self):
        # --- CABECERA ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        title_info = ctk.CTkFrame(header, fg_color="transparent")
        title_info.pack(side="left", anchor="w")
        
        ctk.CTkLabel(title_info, text="Gestión Logística", 
                     font=("Segoe UI", 24, "bold"), text_color="#1A1C1E").pack(anchor="w")
        ctk.CTkLabel(title_info, text="Remisiones, Entradas y Devoluciones", 
                     font=("Segoe UI", 13), text_color="#8A8D91").pack(anchor="w")

        btn_container = ctk.CTkFrame(header, fg_color="transparent")
        btn_container.pack(side="right")

        ctk.CTkButton(btn_container, text="📥 Exportar CSV", fg_color="white", 
                      text_color="#1A1C1E", border_width=1, border_color="#E0E0E0",
                      command=self.export_to_csv, width=120, height=40).pack(side="left", padx=10)

        ctk.CTkButton(btn_container, text="+ Registrar Movimiento", fg_color="#3D5AFE",
                      hover_color="#2A3EB1", height=40, font=("Segoe UI", 13, "bold"),
                      command=self.open_registration_modal).pack(side="left")

        # --- CONTENEDOR DE TABLA CON SCROLL HORIZONTAL ---
        self.table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.table_card.grid(row=1, column=0, sticky="nsew")

        columns = ("date", "type", "product", "qty", "reference")
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(self.table_card, orient="vertical")
        scroll_x = ttk.Scrollbar(self.table_card, orient="horizontal")

        self.tree = ttk.Treeview(
            self.table_card, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Configuración de columnas (Anchos mínimos para forzar scroll si es necesario)
        self.tree.heading("date", text="FECHA")
        self.tree.heading("type", text="OPERACIÓN")
        self.tree.heading("product", text="PRODUCTO")
        self.tree.heading("qty", text="CANT.")
        self.tree.heading("reference", text="DETALLES (DOC / TERCERO / NOTA)")

        self.tree.column("date", width=150, minwidth=150, anchor="center")
        self.tree.column("type", width=120, minwidth=120, anchor="center")
        self.tree.column("product", width=250, minwidth=250, anchor="w")
        self.tree.column("qty", width=80, minwidth=80, anchor="center")
        self.tree.column("reference", width=500, minwidth=400, anchor="w")

        # Layout de tabla y scrolls
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(20,0), pady=(20,0))
        scroll_y.grid(row=0, column=1, sticky="ns", pady=(20,0))
        scroll_x.grid(row=1, column=0, sticky="ew", padx=(20,0), pady=(0,20))

        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(0, weight=1)

    # --- MODAL CON BUSCADOR DE EXTENSIÓN (LISTBOX) ---
    def open_registration_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Registro de Logística")
        modal.geometry("500x700")
        modal.grab_set()
        modal.after(100, lambda: modal.focus_set())

        ctk.CTkLabel(modal, text="Nueva Operación Logística", font=("Segoe UI", 20, "bold")).pack(pady=20)

        # 1. BUSCADOR TIPO GOOGLE (Input + Lista debajo)
        ctk.CTkLabel(modal, text="Buscar Producto (Nombre o SKU):").pack(anchor="w", padx=50)
        
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(modal, textvariable=self.search_var, width=400)
        search_entry.pack(pady=(5, 0))

        # Lista de sugerencias (oculta por defecto)
        self.suggestion_list = ctk.CTkScrollableFrame(modal, width=380, height=120, fg_color="#F2F4F7", corner_radius=0)
        self.selected_product_id = None

        def on_key_release(event):
            term = self.search_var.get().lower()
            # Limpiar lista anterior
            for widget in self.suggestion_list.winfo_children():
                widget.destroy()

            if len(term) > 0:
                matches = [p for p in self.inventory._products.values() 
                           if term in p.name.lower() or term in p.sku.lower()]
                
                if matches:
                    self.suggestion_list.pack(pady=(0, 10))
                    for p in matches:
                        btn = ctk.CTkButton(
                            self.suggestion_list, 
                            text=f"{p.sku} - {p.name}", 
                            fg_color="transparent", 
                            text_color="black",
                            anchor="w",
                            hover_color="#D1D5DB",
                            command=lambda prod=p: select_product(prod)
                        )
                        btn.pack(fill="x")
                else:
                    self.suggestion_list.pack_forget()
            else:
                self.suggestion_list.pack_forget()

        def select_product(prod):
            self.search_var.set(f"{prod.sku} - {prod.name}")
            self.selected_product_id = prod.id
            self.suggestion_list.pack_forget()

        search_entry.bind("<KeyRelease>", on_key_release)

        # 2. OTROS CAMPOS
        ctk.CTkLabel(modal, text="Tipo de Movimiento:").pack(anchor="w", padx=50, pady=(15,0))
        type_mov = ctk.CTkComboBox(modal, values=["Entrada (Compra)", "Remisión (Envío)", "Devolución"], width=400)
        type_mov.pack(pady=5)

        ctk.CTkLabel(modal, text="Tercero (Proveedor/Destinatario):").pack(anchor="w", padx=50, pady=(10,0))
        entry_third = ctk.CTkEntry(modal, width=400)
        entry_third.pack(pady=5)

        ctk.CTkLabel(modal, text="N° Documento Referencia:").pack(anchor="w", padx=50, pady=(10,0))
        entry_doc = ctk.CTkEntry(modal, width=400)
        entry_doc.pack(pady=5)

        ctk.CTkLabel(modal, text="Cantidad:").pack(anchor="w", padx=50, pady=(10,0))
        entry_qty = ctk.CTkEntry(modal, width=400)
        entry_qty.pack(pady=5)

        def confirmar():
            try:
                if not self.selected_product_id: 
                    raise ValueError("Debe seleccionar un producto de la lista")
                
                qty = int(entry_qty.get())
                op_type = type_mov.get()
                mov_dir = "OUT" if "Remisión" in op_type else "IN"
                
                detalles = f"{op_type} | Doc: {entry_doc.get()} | Tercero: {entry_third.get()}"
                
                self.inventory.register_movement(self.selected_product_id, qty, mov_dir, detalles)
                self.refresh()
                modal.destroy()
                messagebox.showinfo("Éxito", "Movimiento registrado.")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        ctk.CTkButton(modal, text="Confirmar Movimiento", fg_color="#3D5AFE", height=45, command=confirmar).pack(pady=30, padx=50, fill="x")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.inventory._history:
            return

        for t in reversed(self.inventory._history):
            p = self.inventory._products.get(t.product_id)
            p_name = f"{p.name} ({p.sku})" if p else "Producto N/A"
            
            # Estilos de etiquetas
            if "Entrada" in t.reason:
                tag = "ENTRADA"
            elif "Remisión" in t.reason:
                tag = "REMISIÓN"
            else:
                tag = "DEVOLUCIÓN"
            
            prefix = "+" if t.type == "IN" else "-"

            self.tree.insert("", "end", values=(
                t.timestamp,
                tag,
                p_name,
                f"{prefix}{t.quantity}",
                t.reason
            ))

    def export_to_csv(self):
        try:
            folder = os.path.join("data", "reportes")
            os.makedirs(folder, exist_ok=True)
            filename = f"reporte-{datetime.now().strftime('%d-%m-%Y_%H-%M')}.csv"
            path = os.path.join(folder, filename)
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Fecha", "Operación", "Producto", "Cantidad", "Detalles"])
                for row_id in self.tree.get_children():
                    writer.writerow(self.tree.item(row_id)['values'])
            messagebox.showinfo("Exportar", f"Reporte en: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo: {e}")