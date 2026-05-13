from conexion import Conexion
from entidades.hito import Hito


class HitoDAO:

    @classmethod
    def listar_por_campana(cls, campana_id):
        conn = None
        cursor = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM hitos_campana WHERE campana_id = %s ORDER BY fecha_hora",
                (campana_id,)
            )
            rows = cursor.fetchall()
            return [Hito(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error listar hitos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        conn = None
        cursor = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM hitos_campana WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Hito(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener hito: {e}")
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, hito):
        conn = None
        cursor = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """INSERT INTO hitos_campana
                     (campana_id, titulo, descripcion, lugar, fecha_hora, estado)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                hito.campana_id, hito.titulo, hito.descripcion,
                hito.lugar, hito.fecha_hora, hito.estado
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar hito: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def marcar_hecho(cls, id):
        conn = None
        cursor = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE hitos_campana SET estado='hecho' WHERE id=%s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error marcar hito hecho: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def postergar(cls, id, nueva_fecha, motivo):
        conn = None
        cursor = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """UPDATE hitos_campana
                     SET estado='postergado', fecha_posterg=%s, motivo_posterg=%s
                     WHERE id=%s"""
            cursor.execute(sql, (nueva_fecha, motivo, id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error postergar hito: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        cursor = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hitos_campana WHERE id=%s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar hito: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)