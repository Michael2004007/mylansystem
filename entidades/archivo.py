class Archivo:
    def __init__(self, id, carpeta_id, nombre, tipo, ruta,
                 tamano_kb=0, created_at=None):
        self.id         = id
        self.carpeta_id = carpeta_id
        self.nombre     = nombre
        self.tipo       = tipo
        self.ruta       = ruta
        self.tamano_kb  = tamano_kb
        self.created_at = created_at

    def __str__(self):
        return f"ID: {self.id} | Archivo: {self.nombre} | Tipo: {self.tipo}"