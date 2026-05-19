class Permiso:
    def __init__(self, id=None, usuario_id=None, modulo=None,
                 puede_ver=True, puede_editar=False, puede_aprobar=False):
        self.id = id
        self.usuario_id = usuario_id
        self.modulo = modulo
        self.puede_ver = puede_ver
        self.puede_editar = puede_editar
        self.puede_aprobar = puede_aprobar
