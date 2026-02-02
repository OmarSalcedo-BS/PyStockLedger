import customtkinter as ctk
from src.core.inventory import Inventory
from src.gui.views.dashboard import DashboardView
from src.gui.views.inventory import InventoryView
from src.gui.views.Movements import MovementsView

COLOR_FONDO = "#F2F4F7"
COLOR_SIDEBAR = "#1A1C1E"
COLOR_ACCENT = "#3D5AFE"


class PyStockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyStock ERP v3.0 - Beta")
        self.geometry("1366x768")
        self.configure(fg_color=COLOR_FONDO)

        self.inventory = Inventory()

        # Layout Principal: Sidebar fijo de 240px
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR FIJO ---
        self.sidebar = ctk.CTkFrame(
            self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # SECCIÓN LOGO (Reemplazable)
        self.logo_placeholder = ctk.CTkFrame(
            self.sidebar, width=60, height=60, corner_radius=12, fg_color=COLOR_ACCENT
        )
        self.logo_placeholder.pack(pady=(40, 10))
        ctk.CTkLabel(self.logo_placeholder, text="📦", font=("Segoe UI", 30)).place(
            relx=0.5, rely=0.5, anchor="center"
        )

        # Nombre de la App
        ctk.CTkLabel(
            self.sidebar,
            text="PyStock Ledger",
            font=("Segoe UI", 22, "bold"),
            text_color="white",
        ).pack()

        # Label de Empresa Cliente (Dinámico)
        self.lbl_empresa = ctk.CTkLabel(
            self.sidebar,
            text="Nombre de empresa S.A.S",
            font=("Segoe UI", 12),
            text_color="#8A8D91",
        )
        self.lbl_empresa.pack(pady=(0, 40))

        # Menú de Navegación con nombres completos
        self.nav_buttons = {}
        menu_items = [
            ("📊  Dashboard", "dash"),
            ("📋  Inventario", "inv"),
            ("🚚  Movimientos", "mov"),
        ]

        for text, name in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=("Segoe UI", 14),
                height=45,
                anchor="w",
                fg_color="transparent",
                hover_color="#2A2D30",
                command=lambda n=name: self.show_view(n),
            )
            btn.pack(fill="x", padx=20, pady=5)
            self.nav_buttons[name] = btn

        # --- CONTENEDOR DE VISTAS ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Cargar Vistas modulares
        self.views = {
            "dash": DashboardView(self.main_container, self.inventory),
            "inv": InventoryView(self.main_container, self.inventory),
            "mov": MovementsView(self.main_container, self.inventory),
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        self.show_view("dash")

    def show_view(self, name):
        """Cambia la vista y resalta el botón activo."""
        for n, btn in self.nav_buttons.items():
            btn.configure(fg_color=COLOR_ACCENT if n == name else "transparent")

        self.views[name].tkraise()
        if hasattr(self.views[name], "refresh"):
            self.views[name].refresh()

    def on_search_type(self, event=None):
        """Maneja la búsqueda en el Treeview de inventario."""
        criterio = self.search_entry.get()
        # Usamos el método search_products que ya definimos en Inventory
        resultados = self.inventory.search_products(criterio)
        self.update_table(resultados)  # Función para refrescar el Treeview


if __name__ == "__main__":
    app = PyStockApp()
    app.mainloop()
