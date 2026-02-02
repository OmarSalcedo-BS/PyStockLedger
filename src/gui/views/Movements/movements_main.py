import customtkinter as ctk
from tkinter import ttk
from src.utils.conversor_Moneda import format_to_cop


class MovementsMainView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        inventory,
        on_new_inbound,
        on_edit_inbound=None,
        on_new_outbound=None,
        on_edit_outbound=None,
    ):
        super().__init__(master, fg_color="transparent")
        self.inventory = inventory
        self.on_new_inbound = on_new_inbound
        self.on_edit_inbound = on_edit_inbound
        self.on_new_outbound = on_new_outbound
        self.on_edit_outbound = on_edit_outbound

        # Configuración de grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_widgets()
        self.update_table()

    def on_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        idx_visual = self.tree.index(selection[0])
        idx_real = len(self.inventory._history) - 1 - idx_visual

        if idx_real < 0 or idx_real >= len(self.inventory._history):
            return

        transaction = self.inventory._history[idx_real]
        product = self.inventory._products.get(transaction.product_id)

        # 1. INTENTO DE EDICIÓN DE GRUPO (FACTURA COMPLETA - ENTRADA)
        if (
            transaction.type == "IN"
            and "Compra Fac:" in transaction.reason
            and self.on_edit_inbound
        ):
            group = [
                t
                for t in self.inventory._history
                if t.reason == transaction.reason
                and t.timestamp == transaction.timestamp
            ]
            self.on_edit_inbound(group)
            return

        # 2. INTENTO DE EDICIÓN DE GRUPO (REMISIÓN - SALIDA)
        if (
            transaction.type == "OUT"
            and "Traslado " in transaction.reason
            and " -> Dest: " in transaction.reason
            and self.on_edit_outbound
        ):
            group = [
                t
                for t in self.inventory._history
                if t.reason == transaction.reason
                and t.timestamp == transaction.timestamp
            ]
            self.on_edit_outbound(group)
            return

        # 3. FALLBACK: EDICIÓN UNITARIA
        if not product:
            ctk.CTkLabel(self, text="Error: Producto no encontrado").pack()
            return

        self.open_edit_dialog(transaction, product)

    def _create_widgets(self):
        # --- 1. CABECERA ---
        self.header = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20), ipady=10)

        ctk.CTkLabel(
            self.header,
            text="Historial de Movimientos",
            font=("Segoe UI", 22, "bold"),
            text_color="#1A1A1A",
        ).pack(side="left", padx=25, pady=15)

        # Botón para ir a la sub-vista de Entrada (Factura)
        self.btn_inbound = ctk.CTkButton(
            self.header,
            text="+ Registrar Entrada (Factura)",
            fg_color="#28A745",
            hover_color="#10B981",
            height=40,
            font=("Segoe UI", 13, "bold"),
            command=self.on_new_inbound,
        )
        self.btn_inbound.pack(side="right", padx=25)

        self.btn_outbound = ctk.CTkButton(
            self.header,
            text="+ Registrar Remisión",
            fg_color="#DC3545",
            hover_color="#C82333",
            height=40,
            font=("Segoe UI", 13, "bold"),
            command=self.on_new_outbound,
        )
        self.btn_outbound.pack(side="right", padx=25)

        # --- 2. CONTENEDOR DE TABLA ---
        self.table_container = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.table_container.grid(row=1, column=0, sticky="nsew")

        # Estilo del Treeview
        style = ttk.Style()
        style.configure(
            "Movements.Treeview",
            rowheight=40,
            font=("Segoe UI", 10),
            background="white",
            fieldbackground="white",
            borderwidth=0,
        )
        style.configure(
            "Movements.Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#F8F9FA",
            foreground="#333",
        )

        # Columnas Extendidas
        # Columnas Simplificadas con Scroll
        columns = ("date", "reference", "type", "qty", "total", "reason")

        # Scrollbars
        sy = ttk.Scrollbar(self.table_container, orient="vertical")
        sx = ttk.Scrollbar(self.table_container, orient="horizontal")

        self.tree = ttk.Treeview(
            self.table_container,
            columns=columns,
            show="headings",
            style="Movements.Treeview",
            yscrollcommand=sy.set,
            xscrollcommand=sx.set,
        )

        # Configurar Scrollbars
        sy.config(command=self.tree.yview)
        sx.config(command=self.tree.xview)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")

        # HEADERS
        self.tree.heading("date", text="FECHA")
        self.tree.heading("reference", text="PROVEEDOR / REFERENCIA")
        self.tree.heading("type", text="TIPO")
        self.tree.heading("qty", text="CANT.")
        self.tree.heading("total", text="TOTAL")
        self.tree.heading("reason", text="NOTAS")

        # COLUMNS
        self.tree.column("date", width=140, anchor="center")
        self.tree.column("reference", width=250, anchor="w")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("qty", width=60, anchor="center")
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("reason", width=500, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def update_table(self):
        """Llena la tabla con las transacciones del inventario."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Invertimos el historial para ver lo más reciente arriba
        for t in reversed(self.inventory._history):
            product = self.inventory._products.get(t.product_id)
            product_name = product.name if product else f"ID: {t.product_id}"

            # --- DETERMINAR REFERENCIA (Título) ---
            reference = product_name
            if "Prov: " in t.reason:
                try:
                    parts = t.reason.split("Prov: ")
                    reference = parts[1]  # Tomamos el proveedor
                except:
                    pass
            elif "Dest: " in t.reason:
                try:
                    parts = t.reason.split("Dest: ")
                    reference = f"Traslado a {parts[1]}"
                except:
                    pass

            # Formatear el tipo (IN/OUT)
            tipo_texto = "ENTRADA" if t.type == "IN" else "SALIDA"
            fecha = getattr(t, "timestamp", "N/A")

            # Cálculos Financieros Simples (Total)
            qty = t.quantity
            cost = getattr(t, "cost", 0.0)
            if cost == 0.0 and product:
                cost = product.cost  # Fallback

            discount = getattr(t, "discount", 0.0)
            tax_rate = getattr(t, "tax", 0.0)

            unit_base = cost - discount
            unit_final = unit_base * (1 + tax_rate)
            total = unit_final * qty

            self.tree.insert(
                "",
                "end",
                values=(
                    fecha,
                    reference,
                    tipo_texto,
                    qty,
                    format_to_cop(total),
                    t.reason,
                ),
            )
        self.tree.bind("<Double-1>", self.on_double_click)

    def open_edit_dialog(self, transaction, product):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Corregir Movimiento")
        dialog.geometry("400x500")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=f"Editar: {product.name}", font=("Segoe UI", 16, "bold")
        ).pack(pady=10)
        ctk.CTkLabel(
            dialog, text=f"Fecha: {transaction.timestamp}", text_color="gray"
        ).pack()

        def make_entry(lbl, val):
            ctk.CTkLabel(dialog, text=lbl).pack(anchor="w", padx=30, pady=(10, 0))
            e = ctk.CTkEntry(dialog)
            e.insert(0, str(val))
            e.pack(fill="x", padx=30, pady=5)
            return e

        e_qty = make_entry("Cantidad:", transaction.quantity)
        e_cost = make_entry(
            "Costo Unitario (Snapshot):", getattr(transaction, "cost", 0.0)
        )
        e_tax = make_entry("IVA Snapshot (0.19):", getattr(transaction, "tax", 0.19))
        e_reason = make_entry("Razón / Notas:", transaction.reason)

        def save():
            try:
                new_qty = int(e_qty.get())
                new_cost = float(e_cost.get())
                new_tax = float(e_tax.get())
                new_reason = e_reason.get()

                # CORRECCIÓN DE STOCK
                # 1. Revertir efecto del movimiento original
                old_amount = (
                    transaction.quantity
                    if transaction.type == "IN"
                    else -transaction.quantity
                )

                # Restamos lo viejo (restar entrada = quitar; restar salida = añadir)
                product.update_stock(-old_amount)

                # 2. Aplicar nuevo efecto
                new_amount = new_qty if transaction.type == "IN" else -new_qty
                product.update_stock(new_amount)

                # 3. Actualizar Datos en Transacción
                transaction.quantity = new_qty
                transaction.cost = new_cost
                transaction.tax = new_tax
                transaction.reason = new_reason

                # Opcional: Si es el último movimiento, actualizar el producto también?
                # Por ahora, solo actualizamos el registro histórico y el stock total.

                self.inventory.save_to_file()
                self.update_table()
                dialog.destroy()

            except ValueError as e:
                ctk.CTkLabel(dialog, text=f"Error: {e}", text_color="red").pack()

        ctk.CTkButton(
            dialog, text="Guardar Corrección", fg_color="#3D5AFE", command=save
        ).pack(pady=20, fill="x", padx=30)
