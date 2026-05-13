class Colaboracion:
    def __init__(self, id, influencer_id, campana_id, tipo, monto, pct_comision,
                 detalle=None, permuta_tag=None, fecha_entrega=None,
                 codigo_promo=None, pct_descuento=None, created_at=None,
                 estado='pendiente'):
        self.id             = id
        self.influencer_id  = influencer_id
        self.campana_id     = campana_id
        self.tipo           = tipo
        self.monto          = monto
        self.pct_comision   = pct_comision
        self.pct_descuento  = pct_descuento
        self.detalle        = detalle
        self.permuta_tag    = permuta_tag
        self.fecha_entrega  = fecha_entrega
        self.codigo_promo   = codigo_promo
        self.created_at     = created_at
        self.estado         = estado
        # campos extra para joins
        self.influencer_nombre = None
        self.influencer_handle = None
        self.influencer_ig     = None
        self.influencer_wa     = None
        self.campana_nombre    = None

    def __str__(self):
        return f"ID: {self.id} | Influencer ID: {self.influencer_id} | Tipo: {self.tipo} | Estado: {self.estado}"
