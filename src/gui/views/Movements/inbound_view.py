import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from src.utils.conversor_Moneda import format_to_cop


class InboundView(ctk.CTkScrollableFrame):
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
        self.ent_invoice.insert(0, self.edit_package["invoice"])

        prov_name = self.edit_package["provider_name"]
        found_nit = None
        for nit, data in getattr(self.inventory, "_providers", {}).items():
            if data["name"] == prov_name:
                found_nit = nit
                break

        if found_nit:
            self.ent_nit.insert(0, found_nit)
            self._auto_fill_provider(None)
        else:
            self.lbl_provider.configure(text=prov_name, text_color="#111827")

        for t in self.edit_package["transactions"]:
            prod = self.inventory._products.get(t.product_id)
            if prod:
                self.temp_items.append(
                    {
                        "id": prod.id,
                        "sku": prod.sku,
                        "name": prod.name,
                        "qty": t.quantity,
                        "cost": getattr(t, "cost", prod.cost),
                        "tax": getattr(t, "tax", prod.tax_purchase),
                    }
                )
        self._refresh_table()
        self.btn_confirm.configure(text="💾 Guardar Cambios (Sobrescribir)")

    def _create_widgets(self):
        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)

        title = "Editar Entrada" if self.edit_package else "Entrada de Productos"
        ctk.CTkLabel(
            header,
            text=title,
            font=("Segoe UI", 26, "bold"),
            text_color="#111827",
        ).pack(side="left")

        # Botones de Acción
        self.btn_confirm = ctk.CTkButton(
            header,
            text="Confirma y genera la entrada",
            fg_color="#10B981",
            hover_color="#059669",
            font=("Segoe UI", 13, "bold"),
            height=42,
            command=self._process_all,
        )
        self.btn_confirm.pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            header,
            text="Cancelar",
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=("Segoe UI", 13, "bold"),
            height=42,
            command=self.on_back,
        ).pack(side="right")

        # --- PANEL DE INFORMACIÓN DEL PROVEEDOR ---
        info_card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB",
        )
        info_card.pack(fill="x", padx=30, pady=(0, 20))

        # Fila 1: NIT, Nombre, Fecha
        row1 = ctk.CTkFrame(info_card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=10)

        self.ent_nit = self._create_input_field(
            row1, "NIT / Tax ID:", "Ingrese NIT...", width=180
        )
        self.ent_nit.bind("<KeyRelease>", self._auto_fill_provider)

        self.ent_provider = self._create_input_field(
            row1, "Proveedor:", "Nombre del proveedor...", width=280
        )

        # Fecha con visibilidad corregida
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.lbl_date = self._create_display_label(
            row1, "Inbound Date:", fecha_hoy, width=140, bg="#E5E7EB", fg="#111827"
        )

        # Fila 2: Factura, Dirección, Teléfono
        row2 = ctk.CTkFrame(info_card, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        self.ent_invoice = self._create_input_field(
            row2, "Invoice Number:", "Ej: FACT-123", width=180
        )
        self.ent_address = self._create_input_field(
            row2, "Dirección:", "Dirección del proveedor...", width=280
        )
        self.ent_phone = self._create_input_field(
            row2, "Teléfono:", "Contacto...", width=140
        )

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
            placeholder_text="Buscar items por SKU o Nombre",
            height=45,
            corner_radius=10,
        )
        self.search_entry.pack(fill="x", padx=20, pady=15)
        self.search_entry.bind("<KeyRelease>", self._on_search_typing)

        # TABLA DE ITEMS
        self.table_container = ctk.CTkFrame(search_card, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollbars
        sy = ttk.Scrollbar(self.table_container, orient="vertical")
        sx = ttk.Scrollbar(self.table_container, orient="horizontal")

        cols = (
            "sku",
            "name",
            "qty",
            "cost",
            "discount",
            "vat_val",
            "unit_final",
            "total",
        )
        self.tree = ttk.Treeview(
            self.table_container,
            columns=cols,
            show="headings",
            yscrollcommand=sy.set,
            xscrollcommand=sx.set,
            height=8,
        )

        sy.config(command=self.tree.yview)
        sx.config(command=self.tree.xview)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="NOMBRE")
        self.tree.heading("qty", text="CANT")
        self.tree.heading("cost", text="BASE")
        self.tree.heading("discount", text="DESC %")
        self.tree.heading("vat_val", text="IVA ($)")
        self.tree.heading("unit_final", text="UNIT (+IVA)")
        self.tree.heading("total", text="TOTAL")

        self.tree.column("sku", width=100, anchor="center")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("qty", width=60, anchor="center")
        self.tree.column("cost", width=100, anchor="e")
        self.tree.column("discount", width=80, anchor="center")
        self.tree.column("vat_val", width=100, anchor="e")
        self.tree.column("unit_final", width=100, anchor="e")
        self.tree.column("total", width=120, anchor="e")

        self.tree.bind("<Double-1>", self._edit_item_dialog)

        # --- SUMARIO FINANCIERO ---
        self._create_summary_card(self)

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

    def _update_totals_card(self):
        """Calcula y muestra el tarjeta de totales financieros."""
        subtotal_gross = 0.0
        total_discount = 0.0
        total_tax = 0.0

        for item in self.temp_items:
            qty = item["qty"]
            cost = item["cost"]
            tax_rate = item["tax"]
            discount_pct = item.get("discount", 0.0)  # Porcentaje (0-100)

            # Subtotal con IVA antes de descuento
            line_base = qty * cost
            line_tax = line_base * tax_rate
            line_subtotal_with_vat = line_base + line_tax

            # Descuento aplicado al subtotal con IVA
            line_discount = line_subtotal_with_vat * (discount_pct / 100)

            subtotal_gross += line_base
            total_tax += line_tax
            total_discount += line_discount

        subtotal_excl_vat = subtotal_gross
        grand_total = (subtotal_gross + total_tax) - total_discount

        # Update Labels
        self.lbl_subtotal.configure(text=format_to_cop(subtotal_excl_vat))
        self.lbl_tax.configure(text=format_to_cop(total_tax))
        if hasattr(self, "lbl_discount"):
            self.lbl_discount.configure(text=format_to_cop(total_discount))
        self.lbl_total.configure(text=format_to_cop(grand_total))

    def _create_display_label(
        self, master, label, text, width, bg="#F3F4F6", fg="#6B7280"
    ):
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
            text_color=fg,
            corner_radius=6,
            anchor="w",
            padx=10,
        )
        l.pack()
        return l

    def _create_summary_card(self, master):
        card = ctk.CTkFrame(
            master,
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

        add_row("Subtotal (Antes de IVA):", "lbl_subtotal")
        add_row("Total IVA:", "lbl_tax")
        add_row("Descuento Total:", "lbl_discount")
        add_row("GRAN TOTAL:", "lbl_total", is_bold=True)

    # --- EDICIÓN DE CELDAS ---
    def _edit_item_dialog(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        # Encontramos el índice en la lista temp_items
        idx = self.tree.index(selected[0])
        item = self.temp_items[idx]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Item")
        dialog.geometry("350x420")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=f"Editando: {item['sku']}", font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        def make_entry(lbl, val):
            ctk.CTkLabel(dialog, text=lbl).pack(anchor="w", padx=20)
            e = ctk.CTkEntry(dialog)
            e.insert(0, str(val))
            e.pack(fill="x", padx=20, pady=5)
            return e

        e_qty = make_entry("Cantidad:", item["qty"])
        e_cost = make_entry("Costo Unitario ($):", item["cost"])
        e_discount = make_entry("Descuento (%):", item.get("discount", 0.0))
        e_tax = make_entry("IVA (0.19 = 19%):", item["tax"])

        def save_edit():
            try:
                item["qty"] = int(e_qty.get())
                item["cost"] = float(e_cost.get())
                item["discount"] = float(e_discount.get())  # Ahora es porcentaje
                item["tax"] = float(e_tax.get())
                self._refresh_table()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Revise los valores numéricos")

        ctk.CTkButton(
            dialog, text="Guardar Cambios", fg_color="#3D5AFE", command=save_edit
        ).pack(pady=20, fill="x", padx=20)
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

    # --- LÓGICA DE PROVEEDORES ---
    def _auto_fill_provider(self, event):
        nit = self.ent_nit.get().strip()
        providers = getattr(self.inventory, "_providers", {})

        if nit in providers:
            data = providers[nit]
            self._fill_field(self.ent_provider, data.get("name", ""))
            self._fill_field(self.ent_address, data.get("address", ""))
            self._fill_field(self.ent_phone, data.get("phone", ""))
        else:
            # No limpiar los campos, permitir edición manual
            pass

    def _fill_field(self, entry, text):
        """Helper para llenar campos de entrada."""
        entry.delete(0, "end")
        entry.insert(0, str(text))

    # --- SUGERENCIAS DINÁMICAS ---
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
        if not self.suggestion_window:
            self.suggestion_window = ctk.CTkToplevel(self)
            self.suggestion_window.overrideredirect(True)
            self.suggestion_window.attributes("-topmost", True)
            self.listbox = ttk.Treeview(
                self.suggestion_window, columns=("name"), show=""
            )
            self.listbox.pack(fill="both", expand=True)
            self.listbox.bind("<<TreeviewSelect>>", self._on_select_suggestion)

        # Altura ajustada al número de items (35px cada uno)
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
                        "tax": product.tax_purchase,
                    }
                )
                self._refresh_table()
                self.search_entry.delete(0, "end")
            self._close_suggestions()

    def _close_suggestions(self):
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in self.temp_items:
            # Nueva lógica: Descuento como % aplicado al subtotal con IVA
            qty = item["qty"]
            cost = item["cost"]
            discount_pct = item.get("discount", 0.0)  # Ahora es porcentaje (0-100)
            tax_rate = item["tax"]

            # 1. Calcular subtotal con IVA (antes de descuento)
            subtotal_with_vat = cost * (1 + tax_rate)

            # 2. Aplicar descuento porcentual
            discount_amount = subtotal_with_vat * (discount_pct / 100)
            unit_final = subtotal_with_vat - discount_amount

            # 3. Calcular valores para mostrar
            vat_value = cost * tax_rate
            total_line = unit_final * qty

            self.tree.insert(
                "",
                "end",
                values=(
                    item["sku"],
                    item["name"],
                    item["qty"],
                    format_to_cop(cost),
                    f"{discount_pct:.1f}%",
                    format_to_cop(vat_value),
                    format_to_cop(unit_final),
                    format_to_cop(total_line),
                ),
            )

        # Actualizamos la tarjeta de totales
        self._update_totals_card()

    # --- PROCESAMIENTO COMPLETO ---
    def _process_all(self):
        nit = self.ent_nit.get().strip()
        invoice = self.ent_invoice.get().strip()
        provider = self.ent_provider.get().strip()
        address = self.ent_address.get().strip()
        phone = self.ent_phone.get().strip()

        if not self.temp_items or not nit or not invoice or not provider:
            messagebox.showwarning(
                "Incompleto", "Verifique productos, NIT, Proveedor y Factura."
            )
            return

        msg = (
            f"¿Sobrescribir entrada con {len(self.temp_items)} items?"
            if self.edit_package
            else f"¿Registrar entrada de {len(self.temp_items)} items?"
        )
        if not messagebox.askyesno("Confirmar", msg):
            return

        try:
            # GUARDAR NUEVO PROVEEDOR SI NO EXISTE
            if nit and nit not in self.inventory._providers:
                self.inventory.save_provider(
                    provider_id=nit, name=provider, address=address, phone=phone
                )
                messagebox.showinfo(
                    "Proveedor Guardado",
                    f"Proveedor '{provider}' guardado exitosamente con NIT: {nit}",
                )

            # SI ES EDICIÓN: PRIMERO ELIMINAMOS LOS MOVIMIENTOS ANTIGUOS
            if self.edit_package:
                old_transactions = self.edit_package["transactions"]
                # Revertir Stock y Eliminar de Historial
                for old_t in old_transactions:
                    # Revertir entrada = Restar cantidad
                    p = self.inventory._products.get(old_t.product_id)
                    if p:
                        if old_t.type == "IN":
                            p.update_stock(-old_t.quantity)
                        else:
                            p.update_stock(old_t.quantity)

                    # Eliminar del historial (por referencia de objeto)
                    # Nota: Debemos buscarlo cuidadosamente si la referencia ha cambiado,
                    # pero como cargamos en memoria, debería ser el mismo objeto.
                    if old_t in self.inventory._history:
                        self.inventory._history.remove(old_t)

            # NUEVO REGISTRO
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reason = f"Compra Fac: {invoice} | Prov: {provider}"

            for item in self.temp_items:
                self.inventory.register_movement(
                    product_id=item["id"],
                    quantity=item["qty"],
                    type="IN",
                    reason=reason,
                    cost=item["cost"],
                    tax=item["tax"],
                    discount=item.get("discount", 0.0),
                    timestamp=now_str,
                )

            self.inventory.save_to_file()
            messagebox.showinfo("Éxito", "Inventario actualizado correctamente.")
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
