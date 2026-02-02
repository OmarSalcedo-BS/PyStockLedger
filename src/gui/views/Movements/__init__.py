import customtkinter as ctk
from .movements_main import MovementsMainView
from .inbound_view import InboundView
from .outbound_view import OutboundView


class MovementsView(ctk.CTkFrame):
    def __init__(self, master, inventory):
        super().__init__(master, fg_color="transparent")
        self.inventory = inventory

        # Configuramos el grid para que las subvistas ocupen todo el espacio
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Mostramos el historial por defecto
        self.show_main_history()

    def _clear_frame(self):
        """Limpia todos los widgets del frame actual."""
        for widget in self.winfo_children():
            widget.destroy()

    def show_main_history(self):
        """Muestra la tabla con el historial de movimientos."""
        self._clear_frame()
        # Pasamos callbacks para Nuevo y Editar
        view = MovementsMainView(
            self,
            self.inventory,
            on_new_inbound=self.show_inbound_view,
            on_edit_inbound=self.edit_inbound_entry,
            on_new_outbound=self.show_outbound_view,
            on_edit_outbound=self.edit_outbound_entry,
        )
        view.grid(row=0, column=0, sticky="nsew")

    def show_inbound_view(self, edit_package=None):
        """Muestra la vista de factura (modo nuevo o edición)."""
        self._clear_frame()
        view = InboundView(
            self, self.inventory, self.show_main_history, edit_package=edit_package
        )
        view.grid(row=0, column=0, sticky="nsew")

    def edit_inbound_entry(self, transactions_group):
        """Prepara los datos de un grupo de transacciones y abre el editor."""
        if not transactions_group:
            return

        # Intentamos parsear la Razón para sacar Factura y Proveedor
        # Formato esperado: "Compra Fac: {invoice} | Prov: {provider}"
        first = transactions_group[0]
        try:
            parts = first.reason.split(" | ")
            invoice = parts[0].replace("Compra Fac: ", "")
            provider_name = parts[1].replace("Prov: ", "")

            package = {
                "transactions": transactions_group,
                "invoice": invoice,
                "provider_name": provider_name,
                "timestamp": first.timestamp,  # Para mantener fecha original si se desea
            }
            self.show_inbound_view(package)
        except IndexError:
            # Si el formato no coincide, no podemos editar en modo 'Factura Completa'
            # Podríamos mostrar error o fallback, pero por ahora solo retornamos
            print("No se pudo parsear el grupo de transacciones para edición masiva.")

    def show_outbound_view(self, edit_package=None):
        """Muestra la vista de remisión (modo nuevo o edición)."""
        self._clear_frame()
        view = OutboundView(
            self, self.inventory, self.show_main_history, edit_package=edit_package
        )
        view.grid(row=0, column=0, sticky="nsew")

    def edit_outbound_entry(self, transactions_group):
        """Prepara los datos de un grupo de transacciones y abre el editor de salidas."""
        if not transactions_group:
            return

        first = transactions_group[0]
        try:
            # Formato esperado: "Traslado {rem_no} -> Dest: {dest}"
            parts = first.reason.split(" -> Dest: ")
            rem_no = parts[0].replace("Traslado ", "")
            destination = parts[1]

            package = {
                "transactions": transactions_group,
                "rem_no": rem_no,
                "destination": destination,
                "timestamp": first.timestamp,
            }
            self.show_outbound_view(package)
        except IndexError:
            pass
