class Usuario:
    def __init__(self, id=None, nombre=None, email=None,
                 password_hash=None, rol='usuario', activo=True, created_at=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash
        self.rol = rol  # 'admin' o 'usuario'
        self.activo = activo
        self.created_at = created_at
        self._is_authenticated = True
        self._is_active = activo
        self._is_anonymous = False

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @property
    def is_active(self):
        return self._is_active

    @property
    def is_anonymous(self):
        return self._is_anonymous

    def es_admin(self):
        return self.rol == 'admin'