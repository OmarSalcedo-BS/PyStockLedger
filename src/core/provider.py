class Provider:
    def __init__(self, nit, name, address, phone, email=""):
        self.nit = nit
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email

    def to_dict(self):
        return {
            "nit": self.nit,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email
        }