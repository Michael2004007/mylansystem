class Influencer:
    def __init__(self, id, nombre, estado, handle=None, url_ig=None,
                 whatsapp=None, notas=None, created_at=None):
        self.id         = id
        self.nombre     = nombre
        self.estado     = estado
        self.handle     = handle
        self.url_ig     = url_ig
        self.whatsapp   = whatsapp
        self.notas      = notas
        self.created_at = created_at

    def __str__(self):
        return f"ID: {self.id} | Influencer: {self.nombre} | Estado: {self.estado}"