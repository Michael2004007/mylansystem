class Campana:
    def __init__(self, id, nombre, mes, anio, presupuesto, gastado,
                 descripcion=None, fecha_inicio=None, fecha_fin=None,
                 status='activa', created_at=None):
        self.id           = id
        self.nombre       = nombre
        self.mes          = mes
        self.anio         = anio
        self.presupuesto  = presupuesto
        self.gastado      = gastado
        self.descripcion  = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin    = fecha_fin
        self.status       = status
        self.created_at   = created_at

    def __str__(self):
        return f"ID: {self.id} | Campaña: {self.nombre} | {self.mes}/{self.anio}"