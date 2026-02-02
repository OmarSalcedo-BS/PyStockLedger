import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from src.utils.conversor_Moneda import format_to_cop


class OutboundView(ctk.CTkScrollableFrame):
    def __init__(self, master, inventory, on_back, edit_package=None):
        super().__init__(master, fg_color="#F9FAFB")
        self.inventory = inventory
        self.on_back = on_back
        self.edit_package = edit_package
        self.temp_items = []
        self.suggestion_window = None

        self._create_widgets()

        if self.edit_package:
            self._load_edit_data()

    def _load_edit_data(self):
        # 1. Cargar Campos de Texto
        self.ent_remission_no.insert(0, self.edit_package["rem_no"])
        self.ent_client_name.insert(0, self.edit_package["destination"])

        # Intentar llenar otros datos si existen en el cliente
        # (Opcional: Podríamos buscar en self.inventory._customers si coincide el nombre)

        # 2. Cargar Items
        for t in self.edit_package["transactions"]:
            prod = self.inventory._products.get(t.product_id)
            if prod:
                self.temp_items.append(
                    {
                        "id": prod.id,
                        "sku": prod.sku,
                        "name": prod.name,
                        "qty": t.quantity,
                        "cost": getattr(t, "cost", prod.cost),  # Costo referencial
                        "tax": getattr(t, "tax", prod.tax_sale),
                    }
                )
        self._refresh_table()
        self.btn_confirm.configure(text="💾 Guardar Cambios (Sobrescribir)")

    def _create_widgets(self):
        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)

        title = (
            "Editar Salida" if self.edit_package else "Remisión de Salida / Traslado"
        )
        ctk.CTkLabel(
            header, text=title, font=("Segoe UI", 26, "bold"), text_color="#111827"
        ).pack(side="left")

        # Botón Confirmar
        self.btn_confirm = ctk.CTkButton(
            header,
            text="Generar Remisión",
            fg_color="#3D5AFE",
            hover_color="#2979FF",
            font=("Segoe UI", 13, "bold"),
            height=42,
            command=self._process_all,
        )
        self.btn_confirm.pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            header,
            text="Cancelar",
            fg_color="#EF4444",
            font=("Segoe UI", 13, "bold"),
            height=42,
            command=self.on_back,
        ).pack(side="right")

        # --- PANEL DE CLIENTE ---
        self._create_client_panel()

        # --- BUSCADOR DE PRODUCTOS ---
        search_card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB",
        )
        search_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.search_entry = ctk.CTkEntry(
            search_card,
            placeholder_text="Buscar productos por SKU o Nombre",
            height=45,
            corner_radius=10,
        )
        self.search_entry.pack(fill="x", padx=20, pady=15)
        self.search_entry.bind("<KeyRelease>", self._on_search_typing)

        # TABLA DE ITEMS
        self.table_container = ctk.CTkFrame(search_card, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=20, pady=10)

        sy = ttk.Scrollbar(self.table_container, orient="vertical")
        sx = ttk.Scrollbar(self.table_container, orient="horizontal")

        cols = ("sku", "name", "qty", "unit_price", "total")
        self.tree = ttk.Treeview(
            self.table_container,
            columns=cols,
            show="headings",
            yscrollcommand=sy.set,
            xscrollcommand=sx.set,
            height=10,
        )

        sy.config(command=self.tree.yview)
        sx.config(command=self.tree.xview)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="NOMBRE")
        self.tree.heading("qty", text="CANT")
        self.tree.heading("unit_price", text="P. UNIT (+IVA)")
        self.tree.heading("total", text="TOTAL")

        self.tree.column("sku", width=100, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("unit_price", width=120, anchor="e")
        self.tree.column("total", width=120, anchor="e")

        self.tree.bind("<Double-1>", self._edit_item_dialog)

        # --- TARJETA DE TOTALES ---
        self._create_summary_card()

    # --- HELPERS UI ---
    def _create_input_field(self, master, label, placeholder, width):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(side="left", padx=10)
        ctk.CTkLabel(
            f, text=label, font=("Segoe UI", 11, "bold"), text_color="#6B7280"
        ).pack(anchor="w")
        e = ctk.CTkEntry(f, width=width, height=35, placeholder_text=placeholder)
        e.pack()
        return e

    def _create_display_label(self, master, label, text, width, bg="#F3F4F6"):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(side="left", padx=10)
        ctk.CTkLabel(
            f, text=label, font=("Segoe UI", 11, "bold"), text_color="#6B7280"
        ).pack(anchor="w")
        l = ctk.CTkLabel(
            f,
            text=text,
            width=width,
            height=35,
            fg_color=bg,
            text_color="#111827",
            corner_radius=6,
            anchor="w",
            padx=10,
        )
        l.pack()
        return l

    def _create_summary_card(self):
        """Crea la tarjeta de totales financieros (versión simple para remisiones)."""
        card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB",
        )
        card.pack(fill="x", padx=30, pady=(0, 20))

        # Right aligned layout
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(side="right", padx=20, pady=15)

        def add_row(label, text_var_attr, is_bold=False):
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            font = ("Segoe UI", 12, "bold" if is_bold else "normal")
            color = "#111827" if is_bold else "#6B7280"

            ctk.CTkLabel(row, text=label, font=font, text_color=color).pack(
                side="left", padx=(0, 20)
            )
            lbl = ctk.CTkLabel(row, text="$0.00", font=font, text_color=color)
            lbl.pack(side="right")
            setattr(self, text_var_attr, lbl)

        add_row("Subtotal:", "lbl_subtotal")
        add_row("Total IVA:", "lbl_tax")
        add_row("TOTAL REMISIÓN:", "lbl_total", is_bold=True)

    def _update_totals_card(self):
        """Calcula y actualiza los totales de la remisión."""
        subtotal = 0.0
        total_tax = 0.0

        for item in self.temp_items:
            qty = item["qty"]
            cost = item.get("cost", 0.0)
            tax_rate = item.get("tax", 0.0)

            line_base = qty * cost
            line_tax = line_base * tax_rate

            subtotal += line_base
            total_tax += line_tax

        grand_total = subtotal + total_tax

        # Update Labels
        self.lbl_subtotal.configure(text=format_to_cop(subtotal))
        self.lbl_tax.configure(text=format_to_cop(total_tax))
        self.lbl_total.configure(text=format_to_cop(grand_total))

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.temp_items:
            # Cálculo financiero básico
            cost = item.get("cost", 0.0)
            tax_rate = item.get("tax", 0.0)
            qty = item["qty"]

            unit_price = cost * (1 + tax_rate)
            total = unit_price * qty

            self.tree.insert(
                "",
                "end",
                values=(
                    item["sku"],
                    item["name"],
                    item["qty"],
                    format_to_cop(unit_price),
                    format_to_cop(total),
                ),
            )

        # Actualizar tarjeta de totales
        self._update_totals_card()

    def _edit_item_dialog(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        idx = self.tree.index(selected[0])
        item = self.temp_items[idx]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Cantidad")
        dialog.geometry("300x200")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=f"Editando: {item['name']}", font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        ctk.CTkLabel(dialog, text="Cantidad:").pack(anchor="w", padx=20)
        e_qty = ctk.CTkEntry(dialog)
        e_qty.insert(0, str(item["qty"]))
        e_qty.pack(fill="x", padx=20, pady=5)

        def save_edit():
            try:
                item["qty"] = int(e_qty.get())
                self._refresh_table()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida")

        ctk.CTkButton(
            dialog, text="Guardar", fg_color="#3D5AFE", command=save_edit
        ).pack(pady=10, fill="x", padx=20)

        ctk.CTkButton(
            dialog,
            text="Eliminar Item",
            fg_color="#EF4444",
            command=lambda: [
                self.temp_items.pop(idx),
                self._refresh_table(),
                dialog.destroy(),
            ],
        ).pack(pady=0, fill="x", padx=20)

    # --- PROCESS ALL UPDATE ---
    def _process_all(self):
        """Registra la SALIDA de mercancía."""
        dest = self.ent_client_name.get().strip()
        rem_no = self.ent_remission_no.get().strip()
        customer_id = self.ent_id.get().strip()
        address = self.ent_address.get().strip()
        phone = self.ent_phone.get().strip()

        if not self.temp_items or not dest:
            messagebox.showwarning("Incompleto", "Especifique destino e items.")
            return

        msg = (
            f"¿Sobrescribir salida a {dest}?"
            if self.edit_package
            else f"¿Generar traslado a {dest}?"
        )
        if not messagebox.askyesno("Confirmar", msg):
            return

        try:
            # GUARDAR NUEVO CLIENTE/SUCURSAL SI NO EXISTE
            if customer_id and customer_id not in self.inventory._customers:
                self.inventory.save_customer(
                    customer_id=customer_id, name=dest, address=address, phone=phone
                )
                messagebox.showinfo(
                    "Cliente Guardado",
                    f"Cliente '{dest}' guardado exitosamente con ID: {customer_id}",
                )

            # SI ES EDICIÓN: REVERTIR (SUMAR STOCK QUE SALIÓ) Y BORRAR
            if self.edit_package:
                old_transactions = self.edit_package["transactions"]
                for old_t in old_transactions:
                    # Revertir salida = Sumar cantidad
                    p = self.inventory._products.get(old_t.product_id)
                    if p:
                        p.update_stock(old_t.quantity)  # Devolvemos al inventario

                    if old_t in self.inventory._history:
                        self.inventory._history.remove(old_t)

            # Validar Stock Real (ahora que ya devolvimos lo viejo)
            for item in self.temp_items:
                prod = self.inventory._products.get(item["id"])
                if prod.stock < item["qty"]:
                    raise ValueError(
                        f"Stock insuficiente para {prod.name} (Disponible: {prod.stock})"
                    )

            # NUEVO REGISTRO - TIMESTAMP ÚNICO PARA TODO EL GRUPO
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reason = f"Traslado {rem_no} -> Dest: {dest}"

            for item in self.temp_items:
                self.inventory.register_movement(
                    product_id=item["id"],
                    quantity=item["qty"],
                    type="OUT",
                    reason=reason,
                    timestamp=now_str,
                )

            self.inventory.save_to_file()
            messagebox.showinfo("Éxito", "Movimiento de salida actualizado.")
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al procesar: {e}")

    def _create_client_panel(self):
        # --- PANEL DE CLIENTE / SUCURSAL ---
        info_card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB",
        )
        info_card.pack(fill="x", padx=30, pady=(0, 20))

        row1 = ctk.CTkFrame(info_card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=10)

        # NIT con auto-fill
        self.ent_id = self._create_input_field(
            row1, "NIT / ID (auto-fill):", "Busque en customers...", width=180
        )
        self.ent_id.bind("<KeyRelease>", self._auto_fill_customer)

        self.ent_client_name = self._create_input_field(
            row1, "Cliente / Sucursal:", "Nombre...", width=280
        )

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.lbl_date = self._create_display_label(
            row1, "Fecha de Traslado:", fecha_hoy, width=140, bg="#E5E7EB"
        )

        row2 = ctk.CTkFrame(info_card, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        self.ent_address = self._create_input_field(
            row2, "Dirección Destino:", "Donde se envía...", width=320
        )
        self.ent_phone = self._create_input_field(
            row2, "Teléfono:", "Contacto...", width=140
        )
        self.ent_remission_no = self._create_input_field(
            row2, "N° Remisión:", "REM-001", width=140
        )

    # --- LÓGICA DE BÚSQUEDA ---
    def _auto_fill_customer(self, event):
        term = self.ent_id.get().strip()
        customers = getattr(self.inventory, "_customers", {})

        if term in customers:
            data = customers[term]
            self._fill_field(self.ent_client_name, data.get("name", ""))
            self._fill_field(self.ent_address, data.get("address", ""))
            self._fill_field(self.ent_phone, data.get("phone", ""))

    def _fill_field(self, entry, text):
        entry.delete(0, "end")
        entry.insert(0, str(text))

    def _on_search_typing(self, event):
        term = self.search_entry.get().strip().lower()
        if len(term) < 2:
            self._close_suggestions()
            return

        matches = [
            p
            for p in self.inventory._products.values()
            if term in p.name.lower() or term in p.sku.lower()
        ]

        if matches:
            self._show_suggestions(matches[:5])
        else:
            self._close_suggestions()

    def _show_suggestions(self, matches):
        # Reutilizamos la lógica compacta de altura dinámica
        if not self.suggestion_window:
            self.suggestion_window = ctk.CTkToplevel(self)
            self.suggestion_window.overrideredirect(True)
            self.suggestion_window.attributes("-topmost", True)
            self.listbox = ttk.Treeview(
                self.suggestion_window, columns=("name"), show=""
            )
            self.listbox.pack(fill="both", expand=True)
            self.listbox.bind("<<TreeviewSelect>>", self._on_select_suggestion)

        height = len(matches) * 35
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()
        self.suggestion_window.geometry(
            f"{self.search_entry.winfo_width()}x{height}+{x}+{y}"
        )

        for i in self.listbox.get_children():
            self.listbox.delete(i)
        for p in matches:
            self.listbox.insert(
                "", "end", values=(f"{p.name} ({p.sku})",), tags=(p.id,)
            )

    def _on_select_suggestion(self, event):
        selected = self.listbox.selection()
        if selected:
            p_id = self.listbox.item(selected[0], "tags")[0]
            product = self.inventory._products.get(int(p_id))
            if product:
                self.temp_items.append(
                    {
                        "id": product.id,
                        "sku": product.sku,
                        "name": product.name,
                        "qty": 1,
                        "cost": product.cost,
                        "tax": product.tax_sale,
                    }
                )
                self._refresh_table()
                self.search_entry.delete(0, "end")
            self._close_suggestions()

    def _close_suggestions(self):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
