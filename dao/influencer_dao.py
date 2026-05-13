from conexion import Conexion
from entidades.influencer import Influencer


class InfluencerDAO:

    @classmethod
    def listar(cls, estado=None, busqueda=None):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)

            # Construir query dinámicamente
            sql = "SELECT * FROM influencers WHERE 1=1"
            params = []

            if estado:
                sql += " AND estado = %s"
                params.append(estado)

            if busqueda:
                sql += " AND (nombre LIKE %s OR handle LIKE %s)"
                busqueda_param = f"%{busqueda}%"
                params.append(busqueda_param)
                params.append(busqueda_param)

            sql += " ORDER BY nombre"

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            return [Influencer(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error listar influencers: {e}")
            return []
        finally:
            if cursor is not None:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM influencers WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Influencer(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener influencer: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def existe_por_handle(cls, handle):
        """Verifica si ya existe un influencer con ese handle"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM influencers WHERE handle = %s", (handle,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"❌ Error verificar handle: {e}")
            return False
        finally:
            if cursor is not None:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, influencer):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """INSERT INTO influencers (nombre, handle, url_ig, whatsapp, estado, notas)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (influencer.nombre, influencer.handle, influencer.url_ig,
                                 influencer.whatsapp, influencer.estado, influencer.notas))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar influencer: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor is not None:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, influencer):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """UPDATE influencers SET nombre=%s, handle=%s, url_ig=%s,
                     whatsapp=%s, estado=%s, notas=%s WHERE id=%s"""
            cursor.execute(sql, (influencer.nombre, influencer.handle, influencer.url_ig,
                                 influencer.whatsapp, influencer.estado, influencer.notas,
                                 influencer.id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar influencer: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor is not None:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM influencers WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar influencer: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor is not None:
                cursor.close()
            Conexion.liberar_conexion(conn)