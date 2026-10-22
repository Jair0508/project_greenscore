class Usuario:
    def __init__(self, identificador, nombre, clave, rol, correo=None, telefono=None):
        self.identificador = identificador
        self.nombre = nombre
        self.clave = clave
        self.rol = rol
        self.correo = correo
        self.telefono = telefono

class Vecino(Usuario):
    def __init__(self, dni, nombre, clave, puntos=0, telefono=None):
        super().__init__(dni, nombre, clave, "vecino", telefono=telefono)
        self.puntos = puntos

class Material:
    TASAS = {
        "Plástico": 10,
        "Vidrio": 5,
        "Cartón": 8,
        "Metal": 15
    }

    @staticmethod
    def calcular_puntos(tipo_material, peso_kg):
        puntos_por_kg = Material.TASAS.get(tipo_material, 0)
        return int(peso_kg * puntos_por_kg)