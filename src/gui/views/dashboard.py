import customtkinter as ctk
from tkinter import ttk
from src.utils.conversor_Moneda import format_to_cop


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, inventory):
        super().__init__(parent, fg_color="transparent")
        self.inventory = inventory

        # Configuración de pesos de columnas
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Título Principal
        ctk.CTkLabel(
            self,
            text="Panel de Control",
            font=("Segoe UI", 32, "bold"),
            text_color="#1A1C1E",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))

        self.cards = {}
        self.setup_ui()
        self._create_lower_panels()

    def setup_ui(self):
        """Crea las tarjetas de resumen superiores"""
        self.cards["val"] = self.create_card(0, "Valor Inventario", "#3D5AFE")
        self.cards["low"] = self.create_card(1, "Alertas Stock", "#E63946")
        self.cards["total"] = self.create_card(2, "Total SKUs", "#52AB62")

    def create_card(self, col, title, color):
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=25, height=150)
        card.grid(row=1, column=col, padx=10, sticky="nsew")
        card.grid_propagate(False)

        accent = ctk.CTkFrame(card, width=6, height=40, corner_radius=3, fg_color=color)
        accent.place(x=25, y=20)

        ctk.CTkLabel(
            card, text=title, font=("Segoe UI", 14), text_color="#64748B"
        ).place(x=25, y=65)
        lbl_val = ctk.CTkLabel(
            card, text="---", font=("Segoe UI", 26, "bold"), text_color="#1A1C1E"
        )
        lbl_val.place(x=25, y=95)
        return lbl_val

    def _create_lower_panels(self):
        """Crea la sección inferior dividida en paneles"""
        # --- CONTENEDOR IZQUIERDO ---
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.grid(
            row=2, column=0, columnspan=2, padx=10, pady=15, sticky="nsew"
        )

        # Top 5 Productos
        self.top_card = self._create_section_card(left_container, "Top 5 Productos")
        self.top_list_frame = ctk.CTkFrame(self.top_card, fg_color="transparent")
        self.top_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Historial de Movimientos
        self.recent_card = self._create_section_card(
            left_container, "Movimientos Recientes"
        )
        self._setup_recent_table()

        # --- CONTENEDOR DERECHO ---
        self.alert_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=25)
        self.alert_panel.grid(row=2, column=2, padx=10, pady=15, sticky="nsew")

        alert_header = ctk.CTkFrame(
            self.alert_panel, fg_color="#FEF2F2", corner_radius=25, height=40
        )
        alert_header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(
            alert_header,
            text="BAJO STOCK",
            text_color="#DC2626",
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=8)

        self.alert_list = ctk.CTkFrame(self.alert_panel, fg_color="transparent")
        self.alert_list.pack(fill="both", expand=True, padx=20)

    def _create_section_card(self, master, title):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=25)
        card.pack(fill="both", expand=True, pady=(0, 15))
        ctk.CTkLabel(
            card, text=title, font=("Segoe UI", 16, "bold"), text_color="#1A1C1E"
        ).pack(anchor="w", padx=20, pady=15)
        return card

    def _setup_recent_table(self):
        style = ttk.Style()
        style.configure("Dash.Treeview", rowheight=30, font=("Segoe UI", 9))

        cols = ("Product", "Type", "Qty", "Date")
        self.tree = ttk.Treeview(
            self.recent_card,
            columns=cols,
            show="headings",
            style="Dash.Treeview",
            height=4,
        )

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=80)

        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.tree.tag_configure("in", foreground="#10B981")
        self.tree.tag_configure("out", foreground="#EF4444")

    def refresh(self):
        summary = self.inventory.get_financial_summary()
        low_stock_list = [p for p in self.inventory._products.values() if p.stock < 5]

        self.cards["val"].configure(text=format_to_cop(summary["inventory_cost"]))
        self.cards["low"].configure(text=f"{len(low_stock_list)} críticos")
        self.cards["total"].configure(text=f"{len(self.inventory._products)} items")

        # Alertas
        for widget in self.alert_list.winfo_children():
            widget.destroy()
        for p in low_stock_list[:5]:
            row = ctk.CTkFrame(self.alert_list, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(
                row, text=p.name, font=("Segoe UI", 11, "bold"), text_color="#1A1C1E"
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=f"{p.stock} Left",
                text_color="#DC2626",  # Rojo más vivo
                font=("Segoe UI", 11, "bold"),
            ).pack(side="right")

        # Top Productos
        for widget in self.top_list_frame.winfo_children():
            widget.destroy()
        sorted_products = sorted(
            self.inventory._products.values(), key=lambda x: x.stock, reverse=True
        )[:4]
        for p in sorted_products:
            container = ctk.CTkFrame(self.top_list_frame, fg_color="transparent")
            container.pack(fill="x", pady=2)
            lbls = ctk.CTkFrame(container, fg_color="transparent")
            lbls.pack(fill="x")
            ctk.CTkLabel(
                lbls, text=p.name, font=("Segoe UI", 12), text_color="#1A1C1E"
            ).pack(side="left")
            ctk.CTkLabel(
                lbls,
                text=f"Stock: {p.stock}",
                font=("Segoe UI", 10, "bold"),
                text_color="#3D5AFE",
            ).pack(side="right")
            bar = ctk.CTkProgressBar(
                container,
                height=8,
                progress_color="#3D5AFE",
                fg_color="#F1F5F9",  # Fondo claro para la barra
            )
            bar.set(min(p.stock / 100, 1.0))
            bar.pack(fill="x", pady=2)

        # Historial
        for item in self.tree.get_children():
            self.tree.delete(item)
        for mov in reversed(self.inventory._history[-5:]):
            product = self.inventory._products.get(mov.product_id)
            p_name = product.name if product else f"ID: {mov.product_id}"
            m_date = getattr(mov, "timestamp", "N/A")
            tag = "in" if mov.type == "IN" else "out"
            self.tree.insert(
                "", "end", values=(p_name, mov.type, mov.quantity, m_date), tags=(tag,)
            )
