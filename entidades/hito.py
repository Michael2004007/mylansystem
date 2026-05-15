class Hito:
    def __init__(self, id, campana_id, titulo, fecha_hora, descripcion=None,
                 lugar=None, estado='pendiente', motivo_posterg=None,
                 fecha_posterg=None, created_at=None, historial_postergaciones=None):
        self.id             = id
        self.campana_id     = campana_id
        self.titulo         = titulo
        self.descripcion    = descripcion
        self.lugar          = lugar
        self.fecha_hora     = fecha_hora
        self.estado         = estado
        self.motivo_posterg = motivo_posterg
        self.fecha_posterg  = fecha_posterg
        self.created_at     = created_at
        self.historial_postergaciones = historial_postergaciones or []