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
    # Tarifas expresadas en puntos por kilogramo (S/ 0.10 = 1 punto)
    TASAS = {
        "Botellas PET (Agua/Gaseosa)": 6.0,
        "Tapas plásticas (PP/HDPE)": 8.0,
        "Cartón corrugado (Cajas)": 2.0,
        "Papel de cuaderno blanco (Limpio)": 7.0,
        "Cuadernos usados / Impresiones": 4.0,
        "Papel periódico": 3.0,
        "Revistas (Papel couche/plastificado)": 2.0,
        "Latas de aluminio (Gaseosa/Cerveza)": 25.0,
        "Latas de conservas (Hojalata/Fierro)": 2.0,
        "Cables viejos (Cobre/Plástico)": 30.0,
        "Componentes informáticos (Placas)": 20.0
    }

    @staticmethod
    def calcular_puntos(nombre_material, peso_kg):
        """
        Calcula los puntos generados según el tipo de material y peso en kg.
        Retorna el resultado redondeado a 1 decimal para permitir fracciones de punto.
        """
        tasa = Material.TASAS.get(nombre_material, 0.0)
        puntos = tasa * peso_kg
        return round(puntos, 1)