class Customer:
    def __init__(self, name, id_number=None, address="", phone="", local_name=""):
        self.id_number = id_number  # NIT o Cédula (puede ser None)
        self.name = name            # Nombre legal o de persona
        self.address = address
        self.phone = phone
        self.local_name = local_name # Nombre del local/sucursal

    def to_dict(self):
        return {
            "id_number": self.id_number,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "local_name": self.local_name
        }