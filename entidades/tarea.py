class Tarea:
    def __init__(self, id=None, titulo=None, descripcion=None, estado='pendiente',
                 prioridad='media', fecha_entrega=None, fecha_creacion=None,
                 campana_id=None, campana_nombre=None, usuario_id=None, usuario_nombre=None,
                 postergaciones=None, created_at=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = estado
        self.prioridad = prioridad
        self.fecha_entrega = fecha_entrega
        self.fecha_creacion = fecha_creacion
        self.campana_id = campana_id
        self.campana_nombre = campana_nombre
        self.usuario_id = usuario_id
        self.usuario_nombre = usuario_nombre
        self.postergaciones = postergaciones
        self.created_at = created_at

    def __str__(self):
        return f"ID: {self.id} | Tarea: {self.titulo} | Asignado a: {self.usuario_nombre or 'Sin asignar'} | Estado: {self.estado}"