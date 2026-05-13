from conexion import Conexion
from entidades.colaboracion import Colaboracion


class ColaboracionDAO:

    @classmethod
    def _map_row(cls, row):
        inf_nombre = row.pop('influencer_nombre', None)
        inf_handle = row.pop('influencer_handle', None)
        inf_ig = row.pop('influencer_ig', None)
        inf_wa = row.pop('influencer_wa', None)
        camp_nombre = row.pop('campana_nombre', None)

        col = Colaboracion(**row)
        col.influencer_nombre = inf_nombre
        col.influencer_handle = inf_handle
        col.influencer_ig = inf_ig
        col.influencer_wa = inf_wa
        col.campana_nombre = camp_nombre
        return col

    @classmethod
    def listar_todas(cls):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT c.*,
                       i.nombre   AS influencer_nombre,
                       i.handle   AS influencer_handle,
                       i.url_ig   AS influencer_ig,
                       i.whatsapp AS influencer_wa,
                       ca.nombre  AS campana_nombre
                FROM colaboraciones c
                LEFT JOIN influencers i  ON i.id  = c.influencer_id
                LEFT JOIN campanas    ca ON ca.id = c.campana_id
                ORDER BY c.created_at DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [cls._map_row(row) for row in rows]
        except Exception as e:
            print(f"Error listar colaboraciones: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_por_campana(cls, campana_id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT c.*,
                       i.nombre   AS influencer_nombre,
                       i.handle   AS influencer_handle,
                       i.url_ig   AS influencer_ig,
                       i.whatsapp AS influencer_wa,
                       ca.nombre  AS campana_nombre
                FROM colaboraciones c
                LEFT JOIN influencers i  ON i.id  = c.influencer_id
                LEFT JOIN campanas    ca ON ca.id = c.campana_id
                WHERE c.campana_id = %s
                ORDER BY c.created_at DESC
            """
            cursor.execute(sql, (campana_id,))
            rows = cursor.fetchall()
            return [cls._map_row(row) for row in rows]
        except Exception as e:
            print(f"Error listar colaboraciones por campaña: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_activas(cls):
        todas = cls.listar_todas()
        return [c for c in todas if (c.estado != 'hecho' or c.tipo in ('ecom', 'ecommerce'))]

    @classmethod
    def obtener(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM colaboraciones WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Colaboracion(**row) if row else None
        except Exception as e:
            print(f"Error obtener colaboración: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, colab):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """INSERT INTO colaboraciones
                     (influencer_id, campana_id, tipo, detalle, monto, permuta_tag,
                      fecha_entrega, codigo_promo, pct_comision, pct_descuento, estado)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                colab.influencer_id, colab.campana_id, colab.tipo,
                colab.detalle, colab.monto, colab.permuta_tag,
                colab.fecha_entrega, colab.codigo_promo,
                colab.pct_comision, colab.pct_descuento,
                getattr(colab, 'estado', 'pendiente') or 'pendiente'
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error insertar colaboración: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, colab):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """UPDATE colaboraciones
                     SET tipo=%s, monto=%s, pct_comision=%s, pct_descuento=%s,
                         detalle=%s, permuta_tag=%s, fecha_entrega=%s, codigo_promo=%s
                     WHERE id=%s"""
            cursor.execute(sql, (
                colab.tipo, colab.monto, colab.pct_comision, colab.pct_descuento,
                colab.detalle, colab.permuta_tag, colab.fecha_entrega, colab.codigo_promo,
                colab.id
            ))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error actualizar colaboración: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM colaboraciones WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error eliminar colaboración: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def marcar_hecho(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE colaboraciones
                SET estado = 'hecho'
                WHERE id = %s
                  AND tipo NOT IN ('ecom', 'ecommerce')
            """, (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error marcar hecho: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def marcar_pendiente(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE colaboraciones SET estado = 'pendiente' WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error marcar pendiente: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)
