import customtkinter as ctk
from src.core.inventory import Inventory
from src.gui.views.dashboard import DashboardView
from src.gui.views.inventory import InventoryView

COLOR_FONDO = "#F2F4F7"
COLOR_SIDEBAR = "#1A1C1E"

class PyStockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PyStock ERP v2.0 - Beta")
        self.geometry("1250x850")
        self.configure(fg_color=COLOR_FONDO)
        
        self.inventory = Inventory()
        self.sidebar_is_expanded = False 

        # Configuración de Grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=80, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.btn_menu = ctk.CTkButton(self.sidebar, text="☰", width=40, height=40, 
                                      fg_color="#333537", hover_color="#3D5AFE", command=self.toggle_sidebar)
        self.btn_menu.pack(pady=20)

        # --- CONTENEDOR DE VISTAS ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Inicialización de Vistas
        self.views = {
            "dash": DashboardView(self.container, self.inventory),
            "inv": InventoryView(self.container, self.inventory)
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        self.show_view("dash")

    def show_view(self, name):
        self.views[name].tkraise()
        if hasattr(self.views[name], "refresh"):
            self.views[name].refresh()

    def toggle_sidebar(self):
        # Lógica de expansión simplificada para la prueba
        new_width = 220 if not self.sidebar_is_expanded else 80
        self.sidebar.configure(width=new_width)
        self.sidebar_is_expanded = not self.sidebar_is_expanded

if __name__ == "__main__":
    app = PyStockApp()
    app.mainloop()