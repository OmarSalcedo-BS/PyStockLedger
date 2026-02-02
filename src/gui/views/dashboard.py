import customtkinter as ctk
from src.utils.conversor_Moneda import format_to_cop

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, inventory):
        super().__init__(parent, fg_color="transparent")
        self.inventory = inventory
        
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(self, text="Overview", font=("Segoe UI", 32, "bold"), text_color="#1A1C1E").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 30))

        # Cards
        self.cards = {}
        self.setup_ui()

    def setup_ui(self):
        self.cards["val"] = self.create_card(0, "Valor Inventario", "#3D5AFE")
        self.cards["low"] = self.create_card(1, "Alertas Stock", "#E63946")
        self.cards["total"] = self.create_card(2, "Total SKUs", "#52AB62")

    def create_card(self, col, title, color):
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=25, height=180)
        card.grid(row=1, column=col, padx=15, sticky="nsew")
        card.grid_propagate(False)
        
        accent = ctk.CTkFrame(card, width=6, height=40, corner_radius=3, fg_color=color)
        accent.place(x=25, y=25)
        
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 15), text_color="gray").place(x=25, y=75)
        lbl_val = ctk.CTkLabel(card, text="---", font=("Segoe UI", 28, "bold"), text_color="#1A1C1E")
        lbl_val.place(x=25, y=110)
        return lbl_val

    def refresh(self):
        summary = self.inventory.get_financial_summary()
        low = len([p for p in self.inventory._products.values() if p.stock < 5])
        self.cards["val"].configure(text=format_to_cop(summary['inventory_cost']))
        self.cards["low"].configure(text=f"{low} críticos")
        self.cards["total"].configure(text=f"{len(self.inventory._products)} items")