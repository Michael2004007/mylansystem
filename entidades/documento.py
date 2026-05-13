class Documento:
    def __init__(self, id, tipo, datos, pdf_ruta=None, created_at=None):
        self.id         = id
        self.tipo       = tipo
        self.datos      = datos or {}
        self.pdf_ruta   = pdf_ruta
        self.created_at = created_at

    def __str__(self):
        return f"ID: {self.id} | Documento: {self.tipo}"